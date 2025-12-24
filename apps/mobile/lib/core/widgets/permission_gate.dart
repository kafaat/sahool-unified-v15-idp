import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../auth/permission_service.dart';

/// PermissionGate Widget
/// ودجت للتحكم في إظهار/إخفاء العناصر حسب الصلاحيات
///
/// Usage:
/// ```dart
/// PermissionGate(
///   permission: Permission.taskCreate,
///   child: CreateTaskButton(),
/// )
/// ```

class PermissionGate extends ConsumerWidget {
  /// Single permission to check
  final String? permission;

  /// Multiple permissions (any match)
  final List<String>? anyPermissions;

  /// Multiple permissions (all must match)
  final List<String>? allPermissions;

  /// Role to check
  final UserRole? role;

  /// Multiple roles (any match)
  final List<UserRole>? anyRoles;

  /// Child to show if permission granted
  final Widget child;

  /// Fallback widget if permission denied (optional)
  final Widget? fallback;

  /// Whether to hide completely or show fallback
  final bool hideCompletely;

  const PermissionGate({
    super.key,
    this.permission,
    this.anyPermissions,
    this.allPermissions,
    this.role,
    this.anyRoles,
    required this.child,
    this.fallback,
    this.hideCompletely = true,
  }) : assert(
          permission != null ||
              anyPermissions != null ||
              allPermissions != null ||
              role != null ||
              anyRoles != null,
          'At least one permission or role must be specified',
        );

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final permissionService = ref.watch(permissionServiceProvider);

    bool hasAccess = _checkAccess(permissionService);

    if (hasAccess) {
      return child;
    }

    if (hideCompletely) {
      return const SizedBox.shrink();
    }

    return fallback ?? const SizedBox.shrink();
  }

  bool _checkAccess(PermissionService service) {
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

    return true;
  }
}

/// PermissionBuilder - More flexible version with builder
class PermissionBuilder extends ConsumerWidget {
  final String? permission;
  final List<String>? anyPermissions;
  final Widget Function(BuildContext context, bool hasPermission) builder;

  const PermissionBuilder({
    super.key,
    this.permission,
    this.anyPermissions,
    required this.builder,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final permissionService = ref.watch(permissionServiceProvider);

    bool hasAccess = true;

    if (permission != null) {
      hasAccess = permissionService.can(permission!);
    } else if (anyPermissions != null) {
      hasAccess = permissionService.canAny(anyPermissions!);
    }

    return builder(context, hasAccess);
  }
}

/// RoleGate - Show/hide based on role
class RoleGate extends ConsumerWidget {
  final UserRole? role;
  final List<UserRole>? anyRoles;
  final Widget child;
  final Widget? fallback;

  const RoleGate({
    super.key,
    this.role,
    this.anyRoles,
    required this.child,
    this.fallback,
  }) : assert(
          role != null || anyRoles != null,
          'Either role or anyRoles must be specified',
        );

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final permissionService = ref.watch(permissionServiceProvider);

    bool hasAccess = false;

    if (role != null) {
      hasAccess = permissionService.hasRole(role!);
    } else if (anyRoles != null) {
      hasAccess = permissionService.hasAnyRole(anyRoles!);
    }

    if (hasAccess) {
      return child;
    }

    return fallback ?? const SizedBox.shrink();
  }
}

/// AdminOnly - Show only for admins
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
    final permissionService = ref.watch(permissionServiceProvider);

    if (permissionService.isAdmin) {
      return child;
    }

    return fallback ?? const SizedBox.shrink();
  }
}

/// ManagerOnly - Show only for managers and above
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
    final permissionService = ref.watch(permissionServiceProvider);

    if (permissionService.isManager) {
      return child;
    }

    return fallback ?? const SizedBox.shrink();
  }
}

/// SupervisorOnly - Show only for supervisors and above
class SupervisorOnly extends ConsumerWidget {
  final Widget child;
  final Widget? fallback;

  const SupervisorOnly({
    super.key,
    required this.child,
    this.fallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final permissionService = ref.watch(permissionServiceProvider);

    if (permissionService.isSupervisor) {
      return child;
    }

    return fallback ?? const SizedBox.shrink();
  }
}

/// OfflineCapable - Show only if action is allowed offline
class OfflineCapable extends ConsumerWidget {
  final String permission;
  final Widget child;
  final Widget? offlineFallback;
  final bool isOffline;

  const OfflineCapable({
    super.key,
    required this.permission,
    required this.child,
    required this.isOffline,
    this.offlineFallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final permissionService = ref.watch(permissionServiceProvider);

    // Check if user has permission
    if (!permissionService.can(permission)) {
      return const SizedBox.shrink();
    }

    // If offline, check if action is allowed offline
    if (isOffline) {
      // Only sync and photo upload are allowed offline
      final offlinePermissions = {
        Permission.offlineSync,
        Permission.offlinePhotoUpload,
        Permission.taskView,
        Permission.taskEdit,
        Permission.taskComplete,
        Permission.fieldView,
      };

      if (!offlinePermissions.contains(permission)) {
        return offlineFallback ??
            Opacity(
              opacity: 0.5,
              child: IgnorePointer(child: child),
            );
      }
    }

    return child;
  }
}
