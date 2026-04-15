/**
 * SAHOOL Auth Hooks
 * خطافات التوثيق والصلاحيات
 */

// Permissions
export {
  PERMISSIONS,
  ROLES,
  ROLE_PERMISSIONS,
  roleHasPermission,
  getRolePermissions,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  getPermissionsForRoles,
} from './permissions';

export type { Permission, Role } from './permissions';

// Auth Hook
export {
  useAuth,
  useCan,
  useCanAny,
  useCanAll,
  useHasRole,
  AuthContext,
  createAuthContextValue,
} from './useAuth';

export type { User, AuthState, AuthContextValue, AuthProviderProps } from './useAuth';
