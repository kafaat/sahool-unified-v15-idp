// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL RBAC - Role Guards
// نظام التحكم في الوصول المبني على الأدوار - حراس الأدوار
// ═══════════════════════════════════════════════════════════════════════════
//
// This file provides widgets and utilities for role-based UI control.
// Includes widget wrappers, route guards, and action guards.
//
// هذا الملف يوفر الودجات والأدوات للتحكم في الواجهة بناءً على الأدوار.
// يشمل أغلفة الودجات، حراس المسارات، وحراس الإجراءات.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'role_model.dart';
import 'permission_model.dart';
import 'rbac_service.dart';
import 'rbac_providers.dart' hide RouteGuardResult, RouteGuardService;
import 'rbac_config.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Role-Based Widget Wrappers
// أغلفة الودجات المبنية على الأدوار
// ═══════════════════════════════════════════════════════════════════════════

/// Widget that shows content based on role/permission
/// ودجت يعرض المحتوى بناءً على الدور/الصلاحية
class RoleGuard extends ConsumerWidget {
  /// Child widget to show if access is granted
  final Widget child;

  /// Fallback widget if access is denied (optional)
  final Widget? fallback;

  /// Required permission
  final Permission? permission;

  /// Required permissions (any of)
  final List<Permission>? anyPermissions;

  /// Required permissions (all of)
  final List<Permission>? allPermissions;

  /// Required role
  final Role? role;

  /// Required roles (any of)
  final List<Role>? anyRoles;

  /// Minimum required role (hierarchy)
  final Role? minRole;

  /// Whether to hide completely if access denied
  final bool hideCompletely;

  /// Show disabled state instead of hiding
  final bool showDisabled;

  /// Custom access check function
  final bool Function(RbacService)? customCheck;

  const RoleGuard({
    super.key,
    required this.child,
    this.fallback,
    this.permission,
    this.anyPermissions,
    this.allPermissions,
    this.role,
    this.anyRoles,
    this.minRole,
    this.hideCompletely = true,
    this.showDisabled = false,
    this.customCheck,
  }) : assert(
          permission != null ||
              anyPermissions != null ||
              allPermissions != null ||
              role != null ||
              anyRoles != null ||
              minRole != null ||
              customCheck != null,
          'At least one condition must be specified',
        );

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rbacService = ref.watch(rbacServiceProvider);

    final hasAccess = _checkAccess(rbacService);

    if (hasAccess) {
      return child;
    }

    if (showDisabled) {
      return Opacity(
        opacity: 0.5,
        child: IgnorePointer(child: child),
      );
    }

    if (hideCompletely) {
      return const SizedBox.shrink();
    }

    return fallback ?? const SizedBox.shrink();
  }

  bool _checkAccess(RbacService service) {
    // Custom check
    if (customCheck != null && !customCheck!(service)) {
      return false;
    }

    // Check single permission
    if (permission != null && !service.can(permission!)) {
      return false;
    }

    // Check any permissions
    if (anyPermissions != null && !service.canAny(anyPermissions!)) {
      return false;
    }

    // Check all permissions
    if (allPermissions != null && !service.canAll(allPermissions!)) {
      return false;
    }

    // Check single role
    if (role != null && !service.hasRole(role!)) {
      return false;
    }

    // Check any roles
    if (anyRoles != null && !service.hasAnyRole(anyRoles!)) {
      return false;
    }

    // Check minimum role
    if (minRole != null && !service.isAtLeast(minRole!)) {
      return false;
    }

    return true;
  }
}

/// Permission guard - simplified wrapper for permission check
/// حارس الصلاحية - غلاف مبسط للتحقق من الصلاحية
class PermissionGuard extends ConsumerWidget {
  final Permission permission;
  final Widget child;
  final Widget? fallback;
  final bool hideCompletely;

  const PermissionGuard({
    super.key,
    required this.permission,
    required this.child,
    this.fallback,
    this.hideCompletely = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return RoleGuard(
      permission: permission,
      hideCompletely: hideCompletely,
      fallback: fallback,
      child: child,
    );
  }
}

/// Builder version with more control
/// نسخة البناء مع تحكم أكثر
class RoleGuardBuilder extends ConsumerWidget {
  final Widget Function(BuildContext context, bool hasAccess, RbacService service)
      builder;
  final Permission? permission;
  final List<Permission>? anyPermissions;
  final Role? minRole;

  const RoleGuardBuilder({
    super.key,
    required this.builder,
    this.permission,
    this.anyPermissions,
    this.minRole,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rbacService = ref.watch(rbacServiceProvider);

    bool hasAccess = true;

    if (permission != null) {
      hasAccess = hasAccess && rbacService.can(permission!);
    }

    if (anyPermissions != null) {
      hasAccess = hasAccess && rbacService.canAny(anyPermissions!);
    }

    if (minRole != null) {
      hasAccess = hasAccess && rbacService.isAtLeast(minRole!);
    }

    return builder(context, hasAccess, rbacService);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Role-Specific Guards
// حراس خاصة بالأدوار
// ═══════════════════════════════════════════════════════════════════════════

/// Show only for admin users
/// عرض للمدراء فقط
class AdminOnly extends ConsumerWidget {
  final Widget child;
  final Widget? fallback;

  const AdminOnly({
    super.key,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return RoleGuard(
      role: Role.admin,
      fallback: fallback,
      child: child,
    );
  }
}

/// Show only for managers and above
/// عرض للمشرفين وأعلى
class ManagerOnly extends ConsumerWidget {
  final Widget child;
  final Widget? fallback;

  const ManagerOnly({
    super.key,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return RoleGuard(
      minRole: Role.manager,
      fallback: fallback,
      child: child,
    );
  }
}

/// Show only for agronomists and above
/// عرض للمهندسين الزراعيين وأعلى
class AgronomistOnly extends ConsumerWidget {
  final Widget child;
  final Widget? fallback;

  const AgronomistOnly({
    super.key,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return RoleGuard(
      minRole: Role.agronomist,
      fallback: fallback,
      child: child,
    );
  }
}

/// Show only for field workers and above
/// عرض لعمال الحقل وأعلى
class FieldWorkerOnly extends ConsumerWidget {
  final Widget child;
  final Widget? fallback;

  const FieldWorkerOnly({
    super.key,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return RoleGuard(
      minRole: Role.fieldWorker,
      fallback: fallback,
      child: child,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Offline-Aware Guards
// حراس مدركة لحالة الاتصال
// ═══════════════════════════════════════════════════════════════════════════

/// Guard that considers offline mode
/// حارس يعتبر وضع عدم الاتصال
class OfflineAwareGuard extends ConsumerWidget {
  final Permission permission;
  final Widget child;
  final Widget? offlineFallback;
  final Widget? permissionFallback;

  const OfflineAwareGuard({
    super.key,
    required this.permission,
    required this.child,
    this.offlineFallback,
    this.permissionFallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rbacService = ref.watch(rbacServiceProvider);
    final isOffline = ref.watch(isOfflineProvider);

    // Check permission first
    if (!rbacService.can(permission)) {
      return permissionFallback ?? const SizedBox.shrink();
    }

    // Check offline capability
    if (isOffline && !permission.offlineCapable) {
      return offlineFallback ??
          Opacity(
            opacity: 0.5,
            child: Tooltip(
              message: 'Not available offline\nغير متاح بدون اتصال',
              child: IgnorePointer(child: child),
            ),
          );
    }

    return child;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Action Guards
// حراس الإجراءات
// ═══════════════════════════════════════════════════════════════════════════

/// Action button with role-based visibility and state
/// زر إجراء مع رؤية وحالة مبنية على الدور
class ActionGuard extends ConsumerWidget {
  /// The action to check
  final RbacAction action;

  /// Button to show if action allowed
  final Widget child;

  /// Widget to show if action not allowed
  final Widget? fallback;

  /// Whether to show disabled state
  final bool showDisabled;

  /// Callback when action is denied
  final VoidCallback? onDenied;

  const ActionGuard({
    super.key,
    required this.action,
    required this.child,
    this.fallback,
    this.showDisabled = false,
    this.onDenied,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rbacService = ref.watch(rbacServiceProvider);

    final isAllowed = rbacService.isActionAllowed(action);

    if (isAllowed) {
      return child;
    }

    if (showDisabled) {
      return GestureDetector(
        onTap: () {
          final reason = rbacService.getActionDenialReason(
            action,
            locale: Localizations.localeOf(context),
          );
          if (reason != null) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(reason)),
            );
          }
          onDenied?.call();
        },
        child: Opacity(
          opacity: 0.5,
          child: IgnorePointer(child: child),
        ),
      );
    }

    return fallback ?? const SizedBox.shrink();
  }
}

/// Guarded button that wraps ElevatedButton
/// زر محمي يغلف ElevatedButton
class GuardedElevatedButton extends ConsumerWidget {
  final VoidCallback? onPressed;
  final Widget child;
  final Permission? permission;
  final Role? minRole;
  final RbacAction? action;
  final ButtonStyle? style;

  const GuardedElevatedButton({
    super.key,
    required this.onPressed,
    required this.child,
    this.permission,
    this.minRole,
    this.action,
    this.style,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rbacService = ref.watch(rbacServiceProvider);

    bool isAllowed = true;

    if (permission != null) {
      isAllowed = isAllowed && rbacService.can(permission!);
    }

    if (minRole != null) {
      isAllowed = isAllowed && rbacService.isAtLeast(minRole!);
    }

    if (action != null) {
      isAllowed = isAllowed && rbacService.isActionAllowed(action!);
    }

    return ElevatedButton(
      onPressed: isAllowed ? onPressed : null,
      style: style,
      child: child,
    );
  }
}

/// Guarded icon button
/// زر أيقونة محمي
class GuardedIconButton extends ConsumerWidget {
  final VoidCallback? onPressed;
  final Widget icon;
  final Permission? permission;
  final Role? minRole;
  final String? tooltip;
  final bool hideWhenDenied;

  const GuardedIconButton({
    super.key,
    required this.onPressed,
    required this.icon,
    this.permission,
    this.minRole,
    this.tooltip,
    this.hideWhenDenied = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rbacService = ref.watch(rbacServiceProvider);

    bool isAllowed = true;

    if (permission != null) {
      isAllowed = isAllowed && rbacService.can(permission!);
    }

    if (minRole != null) {
      isAllowed = isAllowed && rbacService.isAtLeast(minRole!);
    }

    if (!isAllowed && hideWhenDenied) {
      return const SizedBox.shrink();
    }

    return IconButton(
      onPressed: isAllowed ? onPressed : null,
      icon: icon,
      tooltip: tooltip,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Route Guards
// حراس المسارات
// ═══════════════════════════════════════════════════════════════════════════

/// Route guard result
/// نتيجة حارس المسار
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

  String? getMessage(Locale locale) {
    return locale.languageCode == 'ar' ? denialMessageAr : denialMessage;
  }
}

/// Route guard for checking navigation permissions
/// حارس المسار للتحقق من صلاحيات التنقل
class RouteGuardService {
  final RbacService rbacService;

  RouteGuardService(this.rbacService);

  /// Check if route is allowed
  RouteGuardResult checkRoute(String route) {
    // Get route config
    final routeConfig = RbacRoutes.getRouteConfig(route);

    // Unknown routes are allowed by default
    if (routeConfig == null) {
      return RouteGuardResult.success;
    }

    // Check authentication
    if (routeConfig.requiresAuth && rbacService.user == null) {
      return RouteGuardResult.denied(
        redirectRoute: '/login',
        message: 'Please log in to access this page',
        messageAr: 'يرجى تسجيل الدخول للوصول لهذه الصفحة',
      );
    }

    // Check required role
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

    // Check required permissions
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

  /// Check if screen is allowed
  bool canAccessScreen(AppScreen screen) {
    return rbacService.canAccessScreen(screen);
  }

  /// Get accessible screens for navigation
  List<AppScreen> getAccessibleScreens() {
    return rbacService.accessibleScreens;
  }
}

/// Route guard wrapper widget
/// ودجت غلاف حارس المسار
class RouteGuardWrapper extends ConsumerWidget {
  /// The route being accessed
  final String route;

  /// Child to show if access granted
  final Widget child;

  /// Widget to show if access denied
  final Widget Function(BuildContext, RouteGuardResult)? onDenied;

  /// Callback for navigation on denial
  final void Function(BuildContext, RouteGuardResult)? onNavigate;

  const RouteGuardWrapper({
    super.key,
    required this.route,
    required this.child,
    this.onDenied,
    this.onNavigate,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final routeGuard = ref.watch(routeGuardServiceProvider);
    final result = routeGuard.checkRoute(route);

    if (result.allowed) {
      return child;
    }

    if (onNavigate != null) {
      // Schedule navigation after build
      WidgetsBinding.instance.addPostFrameCallback((_) {
        onNavigate!(context, result);
      });
    }

    if (onDenied != null) {
      return onDenied!(context, result);
    }

    // Default denied page
    return _AccessDeniedPage(result: result);
  }
}

/// Default access denied page
/// صفحة الوصول المرفوض الافتراضية
class _AccessDeniedPage extends StatelessWidget {
  final RouteGuardResult result;

  const _AccessDeniedPage({required this.result});

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final message = result.getMessage(locale) ??
        (locale.languageCode == 'ar' ? 'الوصول مرفوض' : 'Access Denied');

    return Scaffold(
      appBar: AppBar(
        title: Text(locale.languageCode == 'ar' ? 'الوصول مرفوض' : 'Access Denied'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.lock_outline,
                size: 64,
                color: Colors.grey,
              ),
              const SizedBox(height: 16),
              Text(
                message,
                style: Theme.of(context).textTheme.titleMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              if (result.redirectRoute != null)
                ElevatedButton(
                  onPressed: () {
                    Navigator.of(context)
                        .pushReplacementNamed(result.redirectRoute!);
                  },
                  child: Text(
                    locale.languageCode == 'ar' ? 'العودة' : 'Go Back',
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Feature Guard
// حارس الميزات
// ═══════════════════════════════════════════════════════════════════════════

/// Guard for feature flags
/// حارس لعلامات الميزات
class FeatureGuard extends ConsumerWidget {
  final String feature;
  final Widget child;
  final Widget? fallback;

  const FeatureGuard({
    super.key,
    required this.feature,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final rbacService = ref.watch(rbacServiceProvider);

    if (rbacService.hasFeature(feature)) {
      return child;
    }

    return fallback ?? const SizedBox.shrink();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Context Extensions
// امتدادات السياق
// ═══════════════════════════════════════════════════════════════════════════

/// Extension on WidgetRef for easy RBAC access
/// امتداد على WidgetRef للوصول السهل للتحكم في الوصول
extension RbacRefExtension on WidgetRef {
  /// Get RBAC service
  RbacService get rbac => read(rbacServiceProvider);

  /// Check permission
  bool can(Permission permission) => rbac.can(permission);

  /// Check role
  bool hasRole(Role role) => rbac.hasRole(role);

  /// Check minimum role
  bool isAtLeast(Role role) => rbac.isAtLeast(role);

  /// Check if action is allowed
  bool isActionAllowed(RbacAction action) => rbac.isActionAllowed(action);

  /// Check feature flag
  bool hasFeature(String feature) => rbac.hasFeature(feature);
}

/// Extension on BuildContext for showing access denied messages
/// امتداد على BuildContext لعرض رسائل رفض الوصول
extension RbacContextExtension on BuildContext {
  /// Show access denied snackbar
  void showAccessDenied([String? message]) {
    final locale = Localizations.localeOf(this);
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Text(
          message ??
              (locale.languageCode == 'ar'
                  ? 'ليس لديك صلاحية لهذا الإجراء'
                  : 'You do not have permission for this action'),
        ),
        backgroundColor: Colors.red,
      ),
    );
  }

  /// Show offline not available snackbar
  void showOfflineNotAvailable() {
    final locale = Localizations.localeOf(this);
    ScaffoldMessenger.of(this).showSnackBar(
      SnackBar(
        content: Text(
          locale.languageCode == 'ar'
              ? 'هذا الإجراء غير متاح بدون اتصال'
              : 'This action is not available offline',
        ),
        backgroundColor: Colors.orange,
      ),
    );
  }
}
