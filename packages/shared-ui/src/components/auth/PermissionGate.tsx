/**
 * Permission Gate Component
 * مكون بوابة الصلاحيات
 *
 * Controls visibility of UI elements based on user permissions
 */

"use client";

import React from "react";

// Types imported from shared-hooks
type Permission = string;
type Role = string;

export interface PermissionGateProps {
  /**
   * Required permission(s) - user must have at least one
   */
  permission?: Permission | Permission[];

  /**
   * Required role(s) - user must have at least one
   */
  role?: Role | Role[];

  /**
   * If true, user must have ALL permissions/roles (not just one)
   */
  requireAll?: boolean;

  /**
   * Content to show when authorized
   */
  children: React.ReactNode;

  /**
   * Content to show when not authorized (optional)
   */
  fallback?: React.ReactNode;

  /**
   * Auth context value (passed from parent or hook)
   */
  auth: {
    can: (permission: Permission) => boolean;
    canAny: (permissions: Permission[]) => boolean;
    canAll: (permissions: Permission[]) => boolean;
    hasRole: (role: Role) => boolean;
    hasAnyRole: (roles: Role[]) => boolean;
  };
}

/**
 * Permission Gate - Controls visibility based on permissions
 *
 * @example
 * // Single permission
 * <PermissionGate permission="field:edit" auth={auth}>
 *   <EditButton />
 * </PermissionGate>
 *
 * @example
 * // Multiple permissions (any)
 * <PermissionGate permission={['field:edit', 'field:delete']} auth={auth}>
 *   <ManageButtons />
 * </PermissionGate>
 *
 * @example
 * // Multiple permissions (all required)
 * <PermissionGate permission={['field:edit', 'field:delete']} requireAll auth={auth}>
 *   <FullAccessPanel />
 * </PermissionGate>
 *
 * @example
 * // With fallback
 * <PermissionGate permission="report:export" fallback={<UpgradePrompt />} auth={auth}>
 *   <ExportButton />
 * </PermissionGate>
 */
export function PermissionGate({
  permission,
  role,
  requireAll = false,
  children,
  fallback = null,
  auth,
}: PermissionGateProps) {
  const hasAccess = React.useMemo(() => {
    // Check permissions
    if (permission) {
      const permissions = Array.isArray(permission) ? permission : [permission];
      const hasPermissionAccess = requireAll
        ? auth.canAll(permissions)
        : auth.canAny(permissions);

      if (!hasPermissionAccess) return false;
    }

    // Check roles
    if (role) {
      const roles = Array.isArray(role) ? role : [role];
      const hasRoleAccess = requireAll
        ? roles.every((r) => auth.hasRole(r))
        : auth.hasAnyRole(roles);

      if (!hasRoleAccess) return false;
    }

    // If no permission or role specified, allow access
    if (!permission && !role) return true;

    return true;
  }, [permission, role, requireAll, auth]);

  return hasAccess ? <>{children}</> : <>{fallback}</>;
}

/**
 * Higher-order component for permission-based rendering
 */
export function withPermission<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  permission: Permission | Permission[],
  options: { requireAll?: boolean; fallback?: React.ComponentType } = {},
) {
  const { requireAll = false, fallback: FallbackComponent } = options;

  return function PermissionWrappedComponent(
    props: P & { auth: PermissionGateProps["auth"] },
  ) {
    const { auth, ...rest } = props;

    return (
      <PermissionGate
        permission={permission}
        requireAll={requireAll}
        fallback={FallbackComponent ? <FallbackComponent /> : null}
        auth={auth}
      >
        <WrappedComponent {...(rest as P)} />
      </PermissionGate>
    );
  };
}

/**
 * Role Gate - Controls visibility based on roles
 */
export function RoleGate({
  role,
  requireAll = false,
  children,
  fallback = null,
  auth,
}: Omit<PermissionGateProps, "permission"> & { role: Role | Role[] }) {
  return (
    <PermissionGate
      role={role}
      requireAll={requireAll}
      fallback={fallback}
      auth={auth}
    >
      {children}
    </PermissionGate>
  );
}

/**
 * Admin Only Gate - Shortcut for admin-only content
 */
export function AdminGate({
  children,
  fallback = null,
  auth,
}: Pick<PermissionGateProps, "children" | "fallback" | "auth">) {
  return (
    <RoleGate role={["admin", "super_admin"]} fallback={fallback} auth={auth}>
      {children}
    </RoleGate>
  );
}
