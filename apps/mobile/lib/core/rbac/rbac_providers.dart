// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL RBAC - Riverpod Providers
// نظام التحكم في الوصول المبني على الأدوار - مزودات Riverpod
// ═══════════════════════════════════════════════════════════════════════════
//
// This file defines all Riverpod providers for the RBAC system.
// Provides reactive state management for roles, permissions, and access control.
//
// هذا الملف يعرّف جميع مزودات Riverpod لنظام التحكم في الوصول.
// يوفر إدارة حالة تفاعلية للأدوار والصلاحيات والتحكم في الوصول.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'role_model.dart';
import 'permission_model.dart';
import 'rbac_service.dart';
import 'rbac_config.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Core State Providers
// مزودات الحالة الأساسية
// ═══════════════════════════════════════════════════════════════════════════

/// Current RBAC user provider
/// مزود المستخدم الحالي للتحكم في الوصول
final rbacUserProvider = StateNotifierProvider<RbacUserNotifier, RbacUser?>((ref) {
  return RbacUserNotifier();
});

/// RBAC User state notifier
/// مدير حالة مستخدم التحكم في الوصول
class RbacUserNotifier extends StateNotifier<RbacUser?> {
  RbacUserNotifier() : super(null);

  /// Set the current user
  void setUser(RbacUser user) {
    state = user;
  }

  /// Clear the current user (logout)
  void clearUser() {
    state = null;
  }

  /// Update user's role
  void updateRole(Role role) {
    if (state != null) {
      state = state!.copyWith(role: role);
    }
  }

  /// Add custom permission
  void addCustomPermission(Permission permission) {
    if (state != null) {
      state = state!.copyWith(
        customPermissions: {...state!.customPermissions, permission},
      );
    }
  }

  /// Remove custom permission
  void removeCustomPermission(Permission permission) {
    if (state != null) {
      final perms = {...state!.customPermissions};
      perms.remove(permission);
      state = state!.copyWith(customPermissions: perms);
    }
  }

  /// Add denied permission
  void addDeniedPermission(Permission permission) {
    if (state != null) {
      state = state!.copyWith(
        deniedPermissions: {...state!.deniedPermissions, permission},
      );
    }
  }

  /// Update assigned fields
  void updateAssignedFields(List<String> fieldIds) {
    if (state != null) {
      state = state!.copyWith(assignedFieldIds: fieldIds);
    }
  }

  /// Update assigned farms
  void updateAssignedFarms(List<String> farmIds) {
    if (state != null) {
      state = state!.copyWith(assignedFarmIds: farmIds);
    }
  }
}

/// Offline mode provider
/// مزود وضع عدم الاتصال
final isOfflineProvider = StateProvider<bool>((ref) => false);

/// Environment provider
/// مزود البيئة
final environmentProvider = StateProvider<String>((ref) => 'production');

/// Capability token provider
/// مزود رمز القدرات
final capabilityTokenProvider = StateProvider<CapabilityToken?>((ref) => null);

// ═══════════════════════════════════════════════════════════════════════════
// RBAC Configuration Provider
// مزود تكوين التحكم في الوصول
// ═══════════════════════════════════════════════════════════════════════════

/// RBAC configuration provider
/// مزود تكوين التحكم في الوصول
final rbacConfigProvider = StateProvider<RbacConfig>((ref) {
  return DefaultRbacConfig.instance;
});

// ═══════════════════════════════════════════════════════════════════════════
// RBAC Service Provider
// مزود خدمة التحكم في الوصول
// ═══════════════════════════════════════════════════════════════════════════

/// Main RBAC service provider
/// مزود خدمة التحكم في الوصول الرئيسية
final rbacServiceProvider = Provider<RbacService>((ref) {
  final user = ref.watch(rbacUserProvider);
  final config = ref.watch(rbacConfigProvider);
  final environment = ref.watch(environmentProvider);
  final isOffline = ref.watch(isOfflineProvider);
  final capabilityToken = ref.watch(capabilityTokenProvider);

  final service = RbacService(
    user: user,
    config: config,
    environment: environment,
    isOffline: isOffline,
  );

  // Set capability token if available
  if (capabilityToken != null) {
    service.setCapabilityToken(capabilityToken);
  }

  return service;
});

/// Route guard service provider
/// مزود خدمة حارس المسارات
final routeGuardServiceProvider = Provider<RouteGuardService>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return RouteGuardService(rbacService);
});

// ═══════════════════════════════════════════════════════════════════════════
// Derived State Providers
// مزودات الحالة المشتقة
// ═══════════════════════════════════════════════════════════════════════════

/// Current user's role provider
/// مزود دور المستخدم الحالي
final currentRoleProvider = Provider<Role>((ref) {
  final user = ref.watch(rbacUserProvider);
  return user?.role ?? Role.guest;
});

/// Current user's permissions provider
/// مزود صلاحيات المستخدم الحالي
final userPermissionsProvider = Provider<Set<Permission>>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.permissions;
});

/// Permission IDs provider
/// مزود معرفات الصلاحيات
final permissionIdsProvider = Provider<Set<String>>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.permissionIds;
});

/// Accessible screens provider
/// مزود الشاشات المتاحة
final accessibleScreensProvider = Provider<List<AppScreen>>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.accessibleScreens;
});

/// User features provider
/// مزود ميزات المستخدم
final userFeaturesProvider = Provider<Set<String>>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.features;
});

// ═══════════════════════════════════════════════════════════════════════════
// Permission Check Providers
// مزودات التحقق من الصلاحيات
// ═══════════════════════════════════════════════════════════════════════════

/// Check single permission provider
/// مزود التحقق من صلاحية واحدة
final canProvider = Provider.family<bool, Permission>((ref, permission) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.can(permission);
});

/// Check permission by ID provider
/// مزود التحقق من الصلاحية بالمعرف
final canByIdProvider = Provider.family<bool, String>((ref, permissionId) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.canById(permissionId);
});

/// Check role provider
/// مزود التحقق من الدور
final hasRoleProvider = Provider.family<bool, Role>((ref, role) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.hasRole(role);
});

/// Check minimum role provider
/// مزود التحقق من الحد الأدنى للدور
final isAtLeastProvider = Provider.family<bool, Role>((ref, role) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.isAtLeast(role);
});

/// Check feature flag provider
/// مزود التحقق من علامة الميزة
final hasFeatureProvider = Provider.family<bool, String>((ref, feature) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.hasFeature(feature);
});

/// Check action provider
/// مزود التحقق من الإجراء
final isActionAllowedProvider = Provider.family<bool, RbacAction>((ref, action) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.isActionAllowed(action);
});

/// Check screen access provider
/// مزود التحقق من الوصول للشاشة
final canAccessScreenProvider = Provider.family<bool, AppScreen>((ref, screen) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.canAccessScreen(screen);
});

/// Check route access provider
/// مزود التحقق من الوصول للمسار
final canAccessRouteProvider = Provider.family<bool, String>((ref, route) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.canAccessRoute(route);
});

// ═══════════════════════════════════════════════════════════════════════════
// Role-Based State Providers
// مزودات الحالة المبنية على الدور
// ═══════════════════════════════════════════════════════════════════════════

/// Is admin provider
/// مزود هل المستخدم مدير
final isAdminProvider = Provider<bool>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.isAdmin;
});

/// Is manager provider
/// مزود هل المستخدم مشرف
final isManagerProvider = Provider<bool>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.isManager;
});

/// Is agronomist provider
/// مزود هل المستخدم مهندس زراعي
final isAgronomistProvider = Provider<bool>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.isAgronomist;
});

/// Is field worker provider
/// مزود هل المستخدم عامل حقل
final isFieldWorkerProvider = Provider<bool>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.isFieldWorker;
});

// ═══════════════════════════════════════════════════════════════════════════
// ABAC (Attribute-Based) Providers
// مزودات التحكم في الوصول المبني على السمات
// ═══════════════════════════════════════════════════════════════════════════

/// Field access check parameters
class FieldAccessParams {
  final String fieldId;
  final Permission permission;

  const FieldAccessParams({
    required this.fieldId,
    required this.permission,
  });

  @override
  bool operator ==(Object other) =>
      other is FieldAccessParams &&
      other.fieldId == fieldId &&
      other.permission == permission;

  @override
  int get hashCode => fieldId.hashCode ^ permission.hashCode;
}

/// Check field access provider
/// مزود التحقق من الوصول للحقل
final canAccessFieldProvider =
    Provider.family<bool, FieldAccessParams>((ref, params) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.canAccessField(params.fieldId, params.permission);
});

/// Check farm access provider
/// مزود التحقق من الوصول للمزرعة
final canAccessFarmProvider = Provider.family<bool, String>((ref, farmId) {
  final rbacService = ref.watch(rbacServiceProvider);
  return rbacService.canAccessFarm(farmId);
});

// ═══════════════════════════════════════════════════════════════════════════
// Permission Category Providers
// مزودات فئات الصلاحيات
// ═══════════════════════════════════════════════════════════════════════════

/// Can view fields
final canViewFieldsProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.fieldsView));
});

/// Can create fields
final canCreateFieldsProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.fieldsCreate));
});

/// Can edit fields
final canEditFieldsProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.fieldsUpdate));
});

/// Can delete fields
final canDeleteFieldsProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.fieldsDelete));
});

/// Can view tasks
final canViewTasksProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.tasksView));
});

/// Can create tasks
final canCreateTasksProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.tasksCreate));
});

/// Can execute tasks
final canExecuteTasksProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.tasksExecute));
});

/// Can assign tasks
final canAssignTasksProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.tasksAssign));
});

/// Can control irrigation
final canControlIrrigationProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.irrigationControl));
});

/// Can view reports
final canViewReportsProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.reportsView));
});

/// Can export reports
final canExportReportsProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.reportsExport));
});

/// Can manage users
final canManageUsersProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.usersManage));
});

/// Can view billing
final canViewBillingProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.billingView));
});

/// Can manage billing
final canManageBillingProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.billingManage));
});

/// Can view audit
final canViewAuditProvider = Provider<bool>((ref) {
  return ref.watch(canProvider(Permissions.auditView));
});

// ═══════════════════════════════════════════════════════════════════════════
// Navigation Providers
// مزودات التنقل
// ═══════════════════════════════════════════════════════════════════════════

/// Navigation items based on permissions
/// عناصر التنقل بناءً على الصلاحيات
class NavItem {
  final AppScreen screen;
  final String route;
  final String labelEn;
  final String labelAr;
  final dynamic icon;
  final List<Permission> requiredPermissions;

  const NavItem({
    required this.screen,
    required this.route,
    required this.labelEn,
    required this.labelAr,
    required this.icon,
    this.requiredPermissions = const [],
  });
}

/// Default navigation items
final defaultNavItems = [
  const NavItem(
    screen: AppScreen.home,
    route: '/',
    labelEn: 'Home',
    labelAr: 'الرئيسية',
    icon: 'home',
  ),
  const NavItem(
    screen: AppScreen.fields,
    route: '/fields',
    labelEn: 'Fields',
    labelAr: 'الحقول',
    icon: 'grass',
    requiredPermissions: [Permissions.fieldsView],
  ),
  const NavItem(
    screen: AppScreen.tasks,
    route: '/tasks',
    labelEn: 'Tasks',
    labelAr: 'المهام',
    icon: 'task_alt',
    requiredPermissions: [Permissions.tasksView],
  ),
  const NavItem(
    screen: AppScreen.weather,
    route: '/weather',
    labelEn: 'Weather',
    labelAr: 'الطقس',
    icon: 'cloud',
    requiredPermissions: [Permissions.weatherView],
  ),
  const NavItem(
    screen: AppScreen.reports,
    route: '/reports',
    labelEn: 'Reports',
    labelAr: 'التقارير',
    icon: 'assessment',
    requiredPermissions: [Permissions.reportsView],
  ),
  const NavItem(
    screen: AppScreen.settings,
    route: '/settings',
    labelEn: 'Settings',
    labelAr: 'الإعدادات',
    icon: 'settings',
    requiredPermissions: [Permissions.settingsView],
  ),
];

/// Accessible navigation items provider
/// مزود عناصر التنقل المتاحة
final accessibleNavItemsProvider = Provider<List<NavItem>>((ref) {
  final rbacService = ref.watch(rbacServiceProvider);

  return defaultNavItems.where((item) {
    if (item.requiredPermissions.isEmpty) return true;
    return rbacService.canAny(item.requiredPermissions);
  }).toList();
});

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// وظائف مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/// Initialize RBAC from user data (e.g., after login)
/// تهيئة التحكم في الوصول من بيانات المستخدم (مثلاً بعد تسجيل الدخول)
void initializeRbac(
  WidgetRef ref, {
  required String userId,
  required String roleString,
  String? tenantId,
  List<String>? assignedFieldIds,
  List<String>? assignedFarmIds,
  List<String>? customPermissionIds,
}) {
  final user = RbacUser(
    id: userId,
    role: Role.fromString(roleString),
    tenantId: tenantId,
    assignedFieldIds: assignedFieldIds ?? [],
    assignedFarmIds: assignedFarmIds ?? [],
    customPermissions: customPermissionIds
            ?.map((id) => Permissions.findById(id))
            .whereType<Permission>()
            .toSet() ??
        {},
  );

  ref.read(rbacUserProvider.notifier).setUser(user);
}

/// Clear RBAC (e.g., on logout)
/// مسح التحكم في الوصول (مثلاً عند تسجيل الخروج)
void clearRbac(WidgetRef ref) {
  ref.read(rbacUserProvider.notifier).clearUser();
  ref.read(capabilityTokenProvider.notifier).state = null;
}

/// Set offline mode
/// تعيين وضع عدم الاتصال
void setOfflineMode(WidgetRef ref, bool isOffline) {
  ref.read(isOfflineProvider.notifier).state = isOffline;
}

/// Set capability token for offline mode
/// تعيين رمز القدرات لوضع عدم الاتصال
void setCapabilityToken(WidgetRef ref, CapabilityToken token) {
  ref.read(capabilityTokenProvider.notifier).state = token;
}

/// Route guard service class
class RouteGuardService {
  final RbacService rbacService;

  RouteGuardService(this.rbacService);

  /// Check if route is allowed
  RouteGuardResult checkRoute(String route) {
    final routeConfig = RbacRoutes.getRouteConfig(route);

    if (routeConfig == null) {
      return RouteGuardResult.success;
    }

    if (routeConfig.requiresAuth && rbacService.user == null) {
      return RouteGuardResult.denied(
        redirectRoute: '/login',
        message: 'Please log in to access this page',
        messageAr: 'يرجى تسجيل الدخول للوصول لهذه الصفحة',
      );
    }

    if (routeConfig.requiredRole != null) {
      if (!rbacService.isAtLeast(routeConfig.requiredRole!)) {
        return RouteGuardResult.denied(
          redirectRoute: '/',
          message:
              'Access denied. Requires ${routeConfig.requiredRole!.nameEn} role.',
          messageAr:
              'الوصول مرفوض. يتطلب دور ${routeConfig.requiredRole!.nameAr}.',
        );
      }
    }

    if (routeConfig.requiredPermissions.isNotEmpty) {
      if (!rbacService.canAny(routeConfig.requiredPermissions)) {
        return RouteGuardResult.denied(
          redirectRoute: '/',
          message: 'You do not have permission to access this page',
          messageAr: 'ليس لديك صلاحية الوصول لهذه الصفحة',
        );
      }
    }

    return RouteGuardResult.success;
  }

  bool canAccessScreen(AppScreen screen) {
    return rbacService.canAccessScreen(screen);
  }

  List<AppScreen> getAccessibleScreens() {
    return rbacService.accessibleScreens;
  }
}

/// Route guard result
class RouteGuardResult {
  final bool allowed;
  final String? redirectRoute;
  final String? denialMessage;
  final String? denialMessageAr;

  const RouteGuardResult({
    required this.allowed,
    this.redirectRoute,
    this.denialMessage,
    this.denialMessageAr,
  });

  static const RouteGuardResult success = RouteGuardResult(allowed: true);

  factory RouteGuardResult.denied({
    String? redirectRoute,
    String? message,
    String? messageAr,
  }) {
    return RouteGuardResult(
      allowed: false,
      redirectRoute: redirectRoute,
      denialMessage: message,
      denialMessageAr: messageAr,
    );
  }
}
