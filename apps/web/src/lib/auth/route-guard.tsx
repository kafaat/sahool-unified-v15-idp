/**
 * Route Guard Utilities
 * أدوات حماية المسارات
 *
 * Server-side route protection for Next.js App Router
 */

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';

// Types
type Permission = string;
type Role = string;

interface User {
  id: string;
  roles: Role[];
  permissions: Permission[];
  tenantId: string;
}

interface RouteGuardOptions {
  /**
   * Required permission(s)
   */
  permission?: Permission | Permission[];

  /**
   * Required role(s)
   */
  role?: Role | Role[];

  /**
   * Require all permissions/roles (default: false = any)
   */
  requireAll?: boolean;

  /**
   * Redirect URL when unauthorized
   */
  redirectTo?: string;

  /**
   * Custom unauthorized handler
   */
  onUnauthorized?: () => never;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SERVER-SIDE AUTH CHECK
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get current user from server context
 * (Implementation depends on your auth setup)
 */
export async function getCurrentUser(): Promise<User | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get('sahool_token')?.value;

  if (!token) {
    return null;
  }

  try {
    // Decode and validate token
    // This is a placeholder - implement actual JWT validation
    const payload = JSON.parse(atob(token.split('.')[1]));

    return {
      id: payload.sub,
      roles: payload.roles || [],
      permissions: payload.permissions || [],
      tenantId: payload.tenant_id,
    };
  } catch {
    return null;
  }
}

/**
 * Check if user has required access
 */
function checkAccess(
  user: User | null,
  options: RouteGuardOptions
): boolean {
  if (!user) return false;

  const { permission, role, requireAll = false } = options;

  // Check permissions
  if (permission) {
    const permissions = Array.isArray(permission) ? permission : [permission];
    const hasPermissionAccess = requireAll
      ? permissions.every((p) => user.permissions.includes(p))
      : permissions.some((p) => user.permissions.includes(p));

    if (!hasPermissionAccess) return false;
  }

  // Check roles
  if (role) {
    const roles = Array.isArray(role) ? role : [role];
    const hasRoleAccess = requireAll
      ? roles.every((r) => user.roles.includes(r))
      : roles.some((r) => user.roles.includes(r));

    if (!hasRoleAccess) return false;
  }

  return true;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ROUTE GUARDS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Require authentication - redirects to login if not authenticated
 *
 * @example
 * // In a page component
 * export default async function ProtectedPage() {
 *   await requireAuth();
 *   return <div>Protected content</div>;
 * }
 */
export async function requireAuth(
  redirectTo: string = '/login'
): Promise<User> {
  const user = await getCurrentUser();

  if (!user) {
    redirect(redirectTo);
  }

  return user;
}

/**
 * Require specific permission(s)
 *
 * @example
 * export default async function EditFieldPage() {
 *   await requirePermission('field:edit');
 *   return <FieldEditor />;
 * }
 */
export async function requirePermission(
  permission: Permission | Permission[],
  options: Omit<RouteGuardOptions, 'permission'> = {}
): Promise<User> {
  const user = await requireAuth(options.redirectTo);

  if (!checkAccess(user, { ...options, permission })) {
    if (options.onUnauthorized) {
      options.onUnauthorized();
    }
    redirect(options.redirectTo || '/unauthorized');
  }

  return user;
}

/**
 * Require specific role(s)
 *
 * @example
 * export default async function AdminPage() {
 *   await requireRole('admin');
 *   return <AdminDashboard />;
 * }
 */
export async function requireRole(
  role: Role | Role[],
  options: Omit<RouteGuardOptions, 'role'> = {}
): Promise<User> {
  const user = await requireAuth(options.redirectTo);

  if (!checkAccess(user, { ...options, role })) {
    if (options.onUnauthorized) {
      options.onUnauthorized();
    }
    redirect(options.redirectTo || '/unauthorized');
  }

  return user;
}

/**
 * Require admin role
 *
 * @example
 * export default async function SuperAdminPage() {
 *   await requireAdmin();
 *   return <SystemSettings />;
 * }
 */
export async function requireAdmin(
  options: Omit<RouteGuardOptions, 'role'> = {}
): Promise<User> {
  return requireRole(['admin', 'super_admin'], options);
}

// ═══════════════════════════════════════════════════════════════════════════════
// PAGE WRAPPER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Create a protected page wrapper
 *
 * @example
 * const ProtectedPage = withRouteGuard(
 *   MyPageComponent,
 *   { permission: 'field:view' }
 * );
 */
export function withRouteGuard<P extends object>(
  PageComponent: React.ComponentType<P & { user: User }>,
  options: RouteGuardOptions
) {
  return async function GuardedPage(props: P) {
    const user = await getCurrentUser();

    if (!user) {
      redirect(options.redirectTo || '/login');
    }

    if (!checkAccess(user, options)) {
      redirect(options.redirectTo || '/unauthorized');
    }

    return <PageComponent {...props} user={user} />;
  };
}
