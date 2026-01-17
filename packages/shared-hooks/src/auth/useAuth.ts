/**
 * SAHOOL Authentication Hook
 * خطاف التوثيق
 */

"use client";

import { createContext, useContext, useCallback, useMemo } from "react";
import type { Role, Permission } from "./permissions";
import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  getPermissionsForRoles,
} from "./permissions";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface User {
  id: string;
  email: string;
  name: string;
  nameAr?: string;
  roles: Role[];
  tenantId: string;
  tenantName?: string;
  governorate?: string;
  avatarUrl?: string;
  metadata?: Record<string, unknown>;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: Error | null;
}

export interface AuthContextValue extends AuthState {
  // Auth actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;

  // Permission checks
  can: (permission: Permission) => boolean;
  canAny: (permissions: Permission[]) => boolean;
  canAll: (permissions: Permission[]) => boolean;

  // Role checks
  hasRole: (role: Role) => boolean;
  hasAnyRole: (roles: Role[]) => boolean;

  // Utilities
  permissions: Permission[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONTEXT
// ═══════════════════════════════════════════════════════════════════════════════

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Hook to access auth context
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

/**
 * Hook to check single permission
 */
export function useCan(permission: Permission): boolean {
  const { can } = useAuth();
  return can(permission);
}

/**
 * Hook to check multiple permissions (any)
 */
export function useCanAny(permissions: Permission[]): boolean {
  const { canAny } = useAuth();
  return canAny(permissions);
}

/**
 * Hook to check multiple permissions (all)
 */
export function useCanAll(permissions: Permission[]): boolean {
  const { canAll } = useAuth();
  return canAll(permissions);
}

/**
 * Hook to check role
 */
export function useHasRole(role: Role): boolean {
  const { hasRole } = useAuth();
  return hasRole(role);
}

// ═══════════════════════════════════════════════════════════════════════════════
// PROVIDER HELPER
// ═══════════════════════════════════════════════════════════════════════════════

export interface AuthProviderProps {
  children: React.ReactNode;
  initialUser?: User | null;
}

/**
 * Create auth context value from user
 */
export function createAuthContextValue(
  user: User | null,
  isLoading: boolean,
  error: Error | null,
  actions: {
    login: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    refreshToken: () => Promise<void>;
  },
): AuthContextValue {
  const roles = user?.roles ?? [];
  const permissions = getPermissionsForRoles(roles);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    ...actions,

    can: (permission: Permission) => hasPermission(roles, permission),
    canAny: (perms: Permission[]) => hasAnyPermission(roles, perms),
    canAll: (perms: Permission[]) => hasAllPermissions(roles, perms),

    hasRole: (role: Role) => roles.includes(role),
    hasAnyRole: (r: Role[]) => r.some((role) => roles.includes(role)),

    permissions,
  };
}

export { AuthContext };
