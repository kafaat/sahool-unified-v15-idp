/**
 * SAHOOL RBAC Permissions System
 * نظام الصلاحيات والأدوار
 */

// ═══════════════════════════════════════════════════════════════════════════════
// PERMISSION DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════════

export const PERMISSIONS = {
  // Field Management
  FIELD_VIEW: 'field:view',
  FIELD_CREATE: 'field:create',
  FIELD_EDIT: 'field:edit',
  FIELD_DELETE: 'field:delete',

  // NDVI & Satellite
  NDVI_VIEW: 'ndvi:view',
  NDVI_ANALYZE: 'ndvi:analyze',
  SATELLITE_ACCESS: 'satellite:access',

  // Alerts
  ALERT_VIEW: 'alert:view',
  ALERT_ACKNOWLEDGE: 'alert:acknowledge',
  ALERT_RESOLVE: 'alert:resolve',
  ALERT_MANAGE: 'alert:manage',

  // Reports
  REPORT_VIEW: 'report:view',
  REPORT_CREATE: 'report:create',
  REPORT_EXPORT: 'report:export',

  // Advisor
  ADVISOR_VIEW: 'advisor:view',
  ADVISOR_REQUEST: 'advisor:request',

  // Admin Functions
  USER_VIEW: 'user:view',
  USER_CREATE: 'user:create',
  USER_EDIT: 'user:edit',
  USER_DELETE: 'user:delete',

  TENANT_VIEW: 'tenant:view',
  TENANT_MANAGE: 'tenant:manage',

  SETTINGS_VIEW: 'settings:view',
  SETTINGS_EDIT: 'settings:edit',

  // System
  SYSTEM_MONITOR: 'system:monitor',
  SYSTEM_ADMIN: 'system:admin',
} as const;

export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

// ═══════════════════════════════════════════════════════════════════════════════
// ROLE DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════════

export const ROLES = {
  // End Users
  FARMER: 'farmer',
  FIELD_MANAGER: 'field_manager',
  AGRONOMIST: 'agronomist',

  // Organization
  ORG_ADMIN: 'org_admin',
  ORG_VIEWER: 'org_viewer',

  // Platform
  SUPPORT: 'support',
  ADMIN: 'admin',
  SUPER_ADMIN: 'super_admin',
} as const;

export type Role = (typeof ROLES)[keyof typeof ROLES];

// ═══════════════════════════════════════════════════════════════════════════════
// ROLE-PERMISSION MAPPING
// ═══════════════════════════════════════════════════════════════════════════════

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  // Farmer - Basic field access
  [ROLES.FARMER]: [
    PERMISSIONS.FIELD_VIEW,
    PERMISSIONS.NDVI_VIEW,
    PERMISSIONS.ALERT_VIEW,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.ADVISOR_VIEW,
    PERMISSIONS.ADVISOR_REQUEST,
  ],

  // Field Manager - Full field management
  [ROLES.FIELD_MANAGER]: [
    PERMISSIONS.FIELD_VIEW,
    PERMISSIONS.FIELD_CREATE,
    PERMISSIONS.FIELD_EDIT,
    PERMISSIONS.NDVI_VIEW,
    PERMISSIONS.NDVI_ANALYZE,
    PERMISSIONS.ALERT_VIEW,
    PERMISSIONS.ALERT_ACKNOWLEDGE,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.REPORT_CREATE,
    PERMISSIONS.REPORT_EXPORT,
    PERMISSIONS.ADVISOR_VIEW,
    PERMISSIONS.ADVISOR_REQUEST,
  ],

  // Agronomist - Expert access
  [ROLES.AGRONOMIST]: [
    PERMISSIONS.FIELD_VIEW,
    PERMISSIONS.FIELD_EDIT,
    PERMISSIONS.NDVI_VIEW,
    PERMISSIONS.NDVI_ANALYZE,
    PERMISSIONS.SATELLITE_ACCESS,
    PERMISSIONS.ALERT_VIEW,
    PERMISSIONS.ALERT_ACKNOWLEDGE,
    PERMISSIONS.ALERT_RESOLVE,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.REPORT_CREATE,
    PERMISSIONS.REPORT_EXPORT,
    PERMISSIONS.ADVISOR_VIEW,
    PERMISSIONS.ADVISOR_REQUEST,
  ],

  // Organization Admin
  [ROLES.ORG_ADMIN]: [
    PERMISSIONS.FIELD_VIEW,
    PERMISSIONS.FIELD_CREATE,
    PERMISSIONS.FIELD_EDIT,
    PERMISSIONS.FIELD_DELETE,
    PERMISSIONS.NDVI_VIEW,
    PERMISSIONS.NDVI_ANALYZE,
    PERMISSIONS.SATELLITE_ACCESS,
    PERMISSIONS.ALERT_VIEW,
    PERMISSIONS.ALERT_ACKNOWLEDGE,
    PERMISSIONS.ALERT_RESOLVE,
    PERMISSIONS.ALERT_MANAGE,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.REPORT_CREATE,
    PERMISSIONS.REPORT_EXPORT,
    PERMISSIONS.ADVISOR_VIEW,
    PERMISSIONS.ADVISOR_REQUEST,
    PERMISSIONS.USER_VIEW,
    PERMISSIONS.USER_CREATE,
    PERMISSIONS.USER_EDIT,
    PERMISSIONS.SETTINGS_VIEW,
    PERMISSIONS.SETTINGS_EDIT,
  ],

  // Organization Viewer
  [ROLES.ORG_VIEWER]: [
    PERMISSIONS.FIELD_VIEW,
    PERMISSIONS.NDVI_VIEW,
    PERMISSIONS.ALERT_VIEW,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.USER_VIEW,
  ],

  // Support - Platform support staff
  [ROLES.SUPPORT]: [
    PERMISSIONS.FIELD_VIEW,
    PERMISSIONS.NDVI_VIEW,
    PERMISSIONS.ALERT_VIEW,
    PERMISSIONS.ALERT_ACKNOWLEDGE,
    PERMISSIONS.REPORT_VIEW,
    PERMISSIONS.USER_VIEW,
    PERMISSIONS.TENANT_VIEW,
    PERMISSIONS.SYSTEM_MONITOR,
  ],

  // Admin - Platform administrator
  [ROLES.ADMIN]: [
    ...Object.values(PERMISSIONS).filter((p) => p !== PERMISSIONS.SYSTEM_ADMIN),
  ],

  // Super Admin - Full access
  [ROLES.SUPER_ADMIN]: Object.values(PERMISSIONS),
};

// ═══════════════════════════════════════════════════════════════════════════════
// PERMISSION UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Check if a role has a specific permission
 */
export function roleHasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

/**
 * Get all permissions for a role
 */
export function getRolePermissions(role: Role): Permission[] {
  return ROLE_PERMISSIONS[role] ?? [];
}

/**
 * Check if a user with given roles has a permission
 */
export function hasPermission(roles: Role[], permission: Permission): boolean {
  return roles.some((role) => roleHasPermission(role, permission));
}

/**
 * Check if a user has any of the given permissions
 */
export function hasAnyPermission(roles: Role[], permissions: Permission[]): boolean {
  return permissions.some((permission) => hasPermission(roles, permission));
}

/**
 * Check if a user has all of the given permissions
 */
export function hasAllPermissions(roles: Role[], permissions: Permission[]): boolean {
  return permissions.every((permission) => hasPermission(roles, permission));
}

/**
 * Get all unique permissions for multiple roles
 */
export function getPermissionsForRoles(roles: Role[]): Permission[] {
  const permissions = new Set<Permission>();
  roles.forEach((role) => {
    getRolePermissions(role).forEach((p) => permissions.add(p));
  });
  return Array.from(permissions);
}
