// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL RBAC - Configuration
// نظام التحكم في الوصول المبني على الأدوار - التكوين
// ═══════════════════════════════════════════════════════════════════════════
//
// This file defines the role-permission mappings and configuration.
// Can be overridden per environment or tenant.
//
// هذا الملف يحدد ربط الأدوار بالصلاحيات والتكوين.
// يمكن تجاوزه لكل بيئة أو مستأجر.

import 'role_model.dart';
import 'permission_model.dart';

/// Screen identifiers for navigation guard
/// معرفات الشاشات لحارس التنقل
enum AppScreen {
  /// Home/Dashboard screen
  home('home', 'الرئيسية'),

  /// Fields list and management
  fields('fields', 'الحقول'),

  /// Field details
  fieldDetails('field_details', 'تفاصيل الحقل'),

  /// Tasks list and management
  tasks('tasks', 'المهام'),

  /// Task details
  taskDetails('task_details', 'تفاصيل المهمة'),

  /// Weather dashboard
  weather('weather', 'الطقس'),

  /// Irrigation management
  irrigation('irrigation', 'الري'),

  /// NDVI/Satellite imagery
  ndvi('ndvi', 'مؤشر النبات'),

  /// Reports and analytics
  reports('reports', 'التقارير'),

  /// IoT devices
  iot('iot', 'الأجهزة'),

  /// Advisory/Recommendations
  advisory('advisory', 'الاستشارات'),

  /// Chat/Communication
  chat('chat', 'المحادثات'),

  /// Equipment management
  equipment('equipment', 'المعدات'),

  /// Inventory management
  inventory('inventory', 'المخزون'),

  /// User management
  users('users', 'المستخدمين'),

  /// Settings
  settings('settings', 'الإعدادات'),

  /// Billing
  billing('billing', 'الفوترة'),

  /// Audit logs
  audit('audit', 'التدقيق'),

  /// Profile
  profile('profile', 'الملف الشخصي'),

  /// Notifications
  notifications('notifications', 'الإشعارات');

  final String value;
  final String nameAr;

  const AppScreen(this.value, this.nameAr);

  String get nameEn => switch (this) {
        AppScreen.home => 'Home',
        AppScreen.fields => 'Fields',
        AppScreen.fieldDetails => 'Field Details',
        AppScreen.tasks => 'Tasks',
        AppScreen.taskDetails => 'Task Details',
        AppScreen.weather => 'Weather',
        AppScreen.irrigation => 'Irrigation',
        AppScreen.ndvi => 'NDVI',
        AppScreen.reports => 'Reports',
        AppScreen.iot => 'IoT Devices',
        AppScreen.advisory => 'Advisory',
        AppScreen.chat => 'Chat',
        AppScreen.equipment => 'Equipment',
        AppScreen.inventory => 'Inventory',
        AppScreen.users => 'Users',
        AppScreen.settings => 'Settings',
        AppScreen.billing => 'Billing',
        AppScreen.audit => 'Audit',
        AppScreen.profile => 'Profile',
        AppScreen.notifications => 'Notifications',
      };
}

/// RBAC Configuration
/// تكوين التحكم في الوصول
class RbacConfig {
  /// Role to permissions mapping
  final Map<Role, Set<Permission>> rolePermissions;

  /// Screen to required permissions mapping
  final Map<AppScreen, List<Permission>> screenPermissions;

  /// Environment-specific overrides
  final Map<String, Map<Role, Set<Permission>>> environmentOverrides;

  /// Tenant-specific overrides (tenant ID -> role -> permissions)
  final Map<String, Map<Role, Set<Permission>>> tenantOverrides;

  const RbacConfig({
    required this.rolePermissions,
    required this.screenPermissions,
    this.environmentOverrides = const {},
    this.tenantOverrides = const {},
  });

  /// Get permissions for a role (with environment override)
  Set<Permission> getPermissionsForRole(
    Role role, {
    String? environment,
    String? tenantId,
  }) {
    // Check tenant override first
    if (tenantId != null && tenantOverrides.containsKey(tenantId)) {
      final tenantPerms = tenantOverrides[tenantId]?[role];
      if (tenantPerms != null) return tenantPerms;
    }

    // Check environment override
    if (environment != null && environmentOverrides.containsKey(environment)) {
      final envPerms = environmentOverrides[environment]?[role];
      if (envPerms != null) return envPerms;
    }

    // Return default
    return rolePermissions[role] ?? {};
  }

  /// Get required permissions for a screen
  List<Permission> getScreenPermissions(AppScreen screen) {
    return screenPermissions[screen] ?? [];
  }

  /// Check if role can access screen
  bool canAccessScreen(Role role, AppScreen screen) {
    final rolePerms = getPermissionsForRole(role);
    final screenPerms = getScreenPermissions(screen);

    if (screenPerms.isEmpty) return true;

    return screenPerms.any((p) => rolePerms.contains(p));
  }

  /// Get all accessible screens for a role
  List<AppScreen> getAccessibleScreens(Role role) {
    return AppScreen.values.where((screen) => canAccessScreen(role, screen)).toList();
  }
}

/// Default RBAC configuration for SAHOOL
/// التكوين الافتراضي للتحكم في الوصول لسهول
class DefaultRbacConfig {
  /// Default role-permission mapping
  /// ربط الأدوار بالصلاحيات الافتراضي
  static final Map<Role, Set<Permission>> rolePermissions = {
    // ─────────────────────────────────────────────────────────────────────
    // Guest - ضيف
    // ─────────────────────────────────────────────────────────────────────
    Role.guest: {
      Permissions.fieldsView,
      Permissions.weatherView,
    },

    // ─────────────────────────────────────────────────────────────────────
    // Viewer - مشاهد
    // ─────────────────────────────────────────────────────────────────────
    Role.viewer: {
      // Fields
      Permissions.fieldsView,
      // Tasks
      Permissions.tasksView,
      // Weather
      Permissions.weatherView,
      // Irrigation
      Permissions.irrigationView,
      // NDVI
      Permissions.ndviView,
      // Reports
      Permissions.reportsView,
      // IoT
      Permissions.iotView,
      // Advisory
      Permissions.advisoryView,
      // Chat (read only)
      Permissions.chatView,
      // Equipment
      Permissions.equipmentView,
      // Inventory
      Permissions.inventoryView,
      // Settings (view only)
      Permissions.settingsView,
    },

    // ─────────────────────────────────────────────────────────────────────
    // Field Worker - عامل حقل
    // ─────────────────────────────────────────────────────────────────────
    Role.fieldWorker: {
      // All viewer permissions
      Permissions.fieldsView,
      Permissions.tasksView,
      Permissions.weatherView,
      Permissions.irrigationView,
      Permissions.ndviView,
      Permissions.reportsView,
      Permissions.iotView,
      Permissions.advisoryView,
      Permissions.chatView,
      Permissions.equipmentView,
      Permissions.inventoryView,
      Permissions.settingsView,
      // Field Worker specific
      Permissions.tasksExecute,
      Permissions.tasksUpdate,
      Permissions.chatCreate,
      Permissions.inventoryUpdate,
      // Offline capabilities
      Permissions.offlineSync,
      Permissions.offlineExport,
    },

    // ─────────────────────────────────────────────────────────────────────
    // Agronomist - مهندس زراعي
    // ─────────────────────────────────────────────────────────────────────
    Role.agronomist: {
      // All viewer permissions
      Permissions.fieldsView,
      Permissions.tasksView,
      Permissions.weatherView,
      Permissions.irrigationView,
      Permissions.ndviView,
      Permissions.reportsView,
      Permissions.iotView,
      Permissions.advisoryView,
      Permissions.chatView,
      Permissions.equipmentView,
      Permissions.inventoryView,
      Permissions.settingsView,
      // Agronomist specific
      Permissions.advisoryCreate,
      Permissions.reportsCreate,
      Permissions.reportsExport,
      Permissions.ndviCreate,
      Permissions.ndviExport,
      Permissions.tasksCreate,
      Permissions.tasksUpdate,
      Permissions.chatCreate,
      // Offline capabilities
      Permissions.offlineSync,
      Permissions.offlineExport,
    },

    // ─────────────────────────────────────────────────────────────────────
    // Manager - مشرف
    // ─────────────────────────────────────────────────────────────────────
    Role.manager: {
      // All agronomist permissions
      Permissions.fieldsView,
      Permissions.tasksView,
      Permissions.weatherView,
      Permissions.irrigationView,
      Permissions.ndviView,
      Permissions.reportsView,
      Permissions.iotView,
      Permissions.advisoryView,
      Permissions.chatView,
      Permissions.equipmentView,
      Permissions.inventoryView,
      Permissions.settingsView,
      Permissions.advisoryCreate,
      Permissions.reportsCreate,
      Permissions.reportsExport,
      Permissions.ndviCreate,
      Permissions.ndviExport,
      Permissions.tasksCreate,
      Permissions.tasksUpdate,
      Permissions.chatCreate,
      Permissions.offlineSync,
      Permissions.offlineExport,
      // Manager specific
      Permissions.fieldsCreate,
      Permissions.fieldsUpdate,
      Permissions.fieldsDelete,
      Permissions.tasksDelete,
      Permissions.tasksAssign,
      Permissions.tasksExecute,
      Permissions.irrigationCreate,
      Permissions.irrigationUpdate,
      Permissions.irrigationControl,
      Permissions.iotCreate,
      Permissions.iotUpdate,
      Permissions.equipmentCreate,
      Permissions.equipmentUpdate,
      Permissions.equipmentDelete,
      Permissions.inventoryCreate,
      Permissions.inventoryDelete,
      Permissions.usersView,
      Permissions.settingsUpdate,
    },

    // ─────────────────────────────────────────────────────────────────────
    // Admin - مدير
    // ─────────────────────────────────────────────────────────────────────
    Role.admin: {
      // All permissions
      ...Permissions.all.toSet(),
    },
  };

  /// Default screen-permission mapping
  /// ربط الشاشات بالصلاحيات الافتراضي
  static final Map<AppScreen, List<Permission>> screenPermissions = {
    // Home is accessible to all authenticated users
    AppScreen.home: [],
    AppScreen.profile: [],
    AppScreen.notifications: [],

    // Fields
    AppScreen.fields: [Permissions.fieldsView],
    AppScreen.fieldDetails: [Permissions.fieldsView],

    // Tasks
    AppScreen.tasks: [Permissions.tasksView],
    AppScreen.taskDetails: [Permissions.tasksView],

    // Weather
    AppScreen.weather: [Permissions.weatherView],

    // Irrigation
    AppScreen.irrigation: [Permissions.irrigationView],

    // NDVI
    AppScreen.ndvi: [Permissions.ndviView],

    // Reports
    AppScreen.reports: [Permissions.reportsView],

    // IoT
    AppScreen.iot: [Permissions.iotView],

    // Advisory
    AppScreen.advisory: [Permissions.advisoryView],

    // Chat
    AppScreen.chat: [Permissions.chatView],

    // Equipment
    AppScreen.equipment: [Permissions.equipmentView],

    // Inventory
    AppScreen.inventory: [Permissions.inventoryView],

    // Users (manager+)
    AppScreen.users: [Permissions.usersView],

    // Settings
    AppScreen.settings: [Permissions.settingsView],

    // Billing (admin only)
    AppScreen.billing: [Permissions.billingView],

    // Audit (admin only)
    AppScreen.audit: [Permissions.auditView],
  };

  /// Development environment overrides
  /// تجاوزات بيئة التطوير
  static final Map<String, Map<Role, Set<Permission>>> environmentOverrides = {
    'development': {
      // In development, give viewers more permissions for testing
      Role.viewer: {
        ...rolePermissions[Role.viewer]!,
        Permissions.reportsExport,
      },
    },
    'staging': {
      // Staging uses same as production
    },
    'production': {
      // Production uses defaults
    },
  };

  /// Get default configuration instance
  static RbacConfig get instance => RbacConfig(
        rolePermissions: rolePermissions,
        screenPermissions: screenPermissions,
        environmentOverrides: environmentOverrides,
      );
}

/// Navigation routes with role requirements
/// مسارات التنقل مع متطلبات الأدوار
class RbacRoutes {
  /// Route configurations
  static final Map<String, RouteConfig> routes = {
    '/': const RouteConfig(
      screen: AppScreen.home,
      requiredRole: null,
      requiredPermissions: [],
    ),
    '/fields': const RouteConfig(
      screen: AppScreen.fields,
      requiredRole: null,
      requiredPermissions: [Permissions.fieldsView],
    ),
    '/fields/:id': const RouteConfig(
      screen: AppScreen.fieldDetails,
      requiredRole: null,
      requiredPermissions: [Permissions.fieldsView],
    ),
    '/tasks': const RouteConfig(
      screen: AppScreen.tasks,
      requiredRole: null,
      requiredPermissions: [Permissions.tasksView],
    ),
    '/tasks/:id': const RouteConfig(
      screen: AppScreen.taskDetails,
      requiredRole: null,
      requiredPermissions: [Permissions.tasksView],
    ),
    '/weather': const RouteConfig(
      screen: AppScreen.weather,
      requiredRole: null,
      requiredPermissions: [Permissions.weatherView],
    ),
    '/irrigation': const RouteConfig(
      screen: AppScreen.irrigation,
      requiredRole: null,
      requiredPermissions: [Permissions.irrigationView],
    ),
    '/ndvi': const RouteConfig(
      screen: AppScreen.ndvi,
      requiredRole: null,
      requiredPermissions: [Permissions.ndviView],
    ),
    '/reports': const RouteConfig(
      screen: AppScreen.reports,
      requiredRole: null,
      requiredPermissions: [Permissions.reportsView],
    ),
    '/iot': const RouteConfig(
      screen: AppScreen.iot,
      requiredRole: null,
      requiredPermissions: [Permissions.iotView],
    ),
    '/advisory': const RouteConfig(
      screen: AppScreen.advisory,
      requiredRole: null,
      requiredPermissions: [Permissions.advisoryView],
    ),
    '/chat': const RouteConfig(
      screen: AppScreen.chat,
      requiredRole: null,
      requiredPermissions: [Permissions.chatView],
    ),
    '/equipment': const RouteConfig(
      screen: AppScreen.equipment,
      requiredRole: null,
      requiredPermissions: [Permissions.equipmentView],
    ),
    '/inventory': const RouteConfig(
      screen: AppScreen.inventory,
      requiredRole: null,
      requiredPermissions: [Permissions.inventoryView],
    ),
    '/users': const RouteConfig(
      screen: AppScreen.users,
      requiredRole: Role.manager,
      requiredPermissions: [Permissions.usersView],
    ),
    '/settings': const RouteConfig(
      screen: AppScreen.settings,
      requiredRole: null,
      requiredPermissions: [Permissions.settingsView],
    ),
    '/billing': const RouteConfig(
      screen: AppScreen.billing,
      requiredRole: Role.admin,
      requiredPermissions: [Permissions.billingView],
    ),
    '/audit': const RouteConfig(
      screen: AppScreen.audit,
      requiredRole: Role.admin,
      requiredPermissions: [Permissions.auditView],
    ),
  };

  /// Get route config
  static RouteConfig? getRouteConfig(String route) {
    // Exact match
    if (routes.containsKey(route)) {
      return routes[route];
    }

    // Pattern match for routes with parameters
    for (final entry in routes.entries) {
      if (_matchRoute(entry.key, route)) {
        return entry.value;
      }
    }

    return null;
  }

  /// Match route with parameters
  static bool _matchRoute(String pattern, String route) {
    final patternParts = pattern.split('/');
    final routeParts = route.split('/');

    if (patternParts.length != routeParts.length) return false;

    for (var i = 0; i < patternParts.length; i++) {
      if (patternParts[i].startsWith(':')) continue;
      if (patternParts[i] != routeParts[i]) return false;
    }

    return true;
  }
}

/// Route configuration
/// تكوين المسار
class RouteConfig {
  /// Screen this route maps to
  final AppScreen screen;

  /// Minimum required role (null = any authenticated)
  final Role? requiredRole;

  /// Required permissions (any match allows access)
  final List<Permission> requiredPermissions;

  /// Whether route requires authentication
  final bool requiresAuth;

  const RouteConfig({
    required this.screen,
    this.requiredRole,
    this.requiredPermissions = const [],
    this.requiresAuth = true,
  });
}

/// Feature flags for role-based features
/// علامات الميزات للميزات المبنية على الأدوار
class RbacFeatures {
  /// Feature flags by role
  static final Map<Role, Set<String>> featureFlags = {
    Role.guest: {
      'view_public_fields',
      'view_weather',
    },
    Role.viewer: {
      'view_public_fields',
      'view_weather',
      'view_tasks',
      'view_reports',
      'view_ndvi',
    },
    Role.fieldWorker: {
      'view_public_fields',
      'view_weather',
      'view_tasks',
      'view_reports',
      'view_ndvi',
      'execute_tasks',
      'offline_mode',
      'photo_capture',
      'voice_input',
    },
    Role.agronomist: {
      'view_public_fields',
      'view_weather',
      'view_tasks',
      'view_reports',
      'view_ndvi',
      'execute_tasks',
      'offline_mode',
      'photo_capture',
      'voice_input',
      'create_advisory',
      'create_reports',
      'export_data',
      'advanced_analytics',
    },
    Role.manager: {
      'view_public_fields',
      'view_weather',
      'view_tasks',
      'view_reports',
      'view_ndvi',
      'execute_tasks',
      'offline_mode',
      'photo_capture',
      'voice_input',
      'create_advisory',
      'create_reports',
      'export_data',
      'advanced_analytics',
      'manage_fields',
      'manage_tasks',
      'manage_workers',
      'manage_equipment',
      'irrigation_control',
      'iot_management',
    },
    Role.admin: {
      'view_public_fields',
      'view_weather',
      'view_tasks',
      'view_reports',
      'view_ndvi',
      'execute_tasks',
      'offline_mode',
      'photo_capture',
      'voice_input',
      'create_advisory',
      'create_reports',
      'export_data',
      'advanced_analytics',
      'manage_fields',
      'manage_tasks',
      'manage_workers',
      'manage_equipment',
      'irrigation_control',
      'iot_management',
      'user_management',
      'billing_management',
      'audit_access',
      'system_settings',
      'tenant_management',
    },
  };

  /// Check if role has feature
  static bool hasFeature(Role role, String feature) {
    // Admin has all features
    if (role == Role.admin) return true;

    return featureFlags[role]?.contains(feature) ?? false;
  }

  /// Get all features for role
  static Set<String> getFeatures(Role role) {
    return featureFlags[role] ?? {};
  }
}
