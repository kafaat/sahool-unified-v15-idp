import { describe, it, expect } from 'vitest';
import {
  PERMISSIONS,
  ROLES,
  ROLE_PERMISSIONS,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  getRolePermissions,
  roleHasPermission,
  getPermissionsForRoles,
} from './permissions';
import type { Role, Permission } from './permissions';

describe('Permissions', () => {
  describe('PERMISSIONS constant', () => {
    it('should have field permissions', () => {
      expect(PERMISSIONS.FIELD_VIEW).toBe('field:view');
      expect(PERMISSIONS.FIELD_CREATE).toBe('field:create');
      expect(PERMISSIONS.FIELD_EDIT).toBe('field:edit');
      expect(PERMISSIONS.FIELD_DELETE).toBe('field:delete');
    });

    it('should have NDVI permissions', () => {
      expect(PERMISSIONS.NDVI_VIEW).toBe('ndvi:view');
      expect(PERMISSIONS.NDVI_ANALYZE).toBe('ndvi:analyze');
    });

    it('should have alert permissions', () => {
      expect(PERMISSIONS.ALERT_VIEW).toBe('alert:view');
      expect(PERMISSIONS.ALERT_MANAGE).toBe('alert:manage');
      expect(PERMISSIONS.ALERT_ACKNOWLEDGE).toBe('alert:acknowledge');
      expect(PERMISSIONS.ALERT_RESOLVE).toBe('alert:resolve');
    });

    it('should have user management permissions', () => {
      expect(PERMISSIONS.USER_VIEW).toBe('user:view');
      expect(PERMISSIONS.USER_CREATE).toBe('user:create');
      expect(PERMISSIONS.USER_EDIT).toBe('user:edit');
      expect(PERMISSIONS.USER_DELETE).toBe('user:delete');
    });

    it('should have system permissions', () => {
      expect(PERMISSIONS.SYSTEM_MONITOR).toBe('system:monitor');
      expect(PERMISSIONS.SYSTEM_ADMIN).toBe('system:admin');
    });
  });

  describe('ROLES constant', () => {
    it('should have all defined roles', () => {
      expect(ROLES.FARMER).toBe('farmer');
      expect(ROLES.AGRONOMIST).toBe('agronomist');
      expect(ROLES.ADMIN).toBe('admin');
      expect(ROLES.SUPER_ADMIN).toBe('super_admin');
      expect(ROLES.FIELD_MANAGER).toBe('field_manager');
      expect(ROLES.ORG_ADMIN).toBe('org_admin');
    });
  });

  describe('roleHasPermission', () => {
    it('should return true when role has the permission', () => {
      expect(roleHasPermission(ROLES.FARMER, PERMISSIONS.FIELD_VIEW)).toBe(true);
      expect(roleHasPermission(ROLES.FARMER, PERMISSIONS.NDVI_VIEW)).toBe(true);
    });

    it('should return false when role lacks the permission', () => {
      expect(roleHasPermission(ROLES.FARMER, PERMISSIONS.FIELD_DELETE)).toBe(false);
      expect(roleHasPermission(ROLES.FARMER, PERMISSIONS.SYSTEM_ADMIN)).toBe(false);
    });
  });

  describe('hasPermission', () => {
    it('should return true when any role has the permission', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasPermission(roles, PERMISSIONS.FIELD_VIEW)).toBe(true);
      expect(hasPermission(roles, PERMISSIONS.ALERT_VIEW)).toBe(true);
    });

    it('should return false when no role has the permission', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasPermission(roles, PERMISSIONS.FIELD_DELETE)).toBe(false);
      expect(hasPermission(roles, PERMISSIONS.SYSTEM_ADMIN)).toBe(false);
    });

    it('should return false for empty roles array', () => {
      expect(hasPermission([], PERMISSIONS.FIELD_VIEW)).toBe(false);
    });

    it('should check multiple roles', () => {
      const roles: Role[] = [ROLES.FARMER, ROLES.FIELD_MANAGER];
      expect(hasPermission(roles, PERMISSIONS.FIELD_CREATE)).toBe(true);
    });
  });

  describe('hasAnyPermission', () => {
    it('should return true when user has any of the permissions', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasAnyPermission(roles, [PERMISSIONS.FIELD_VIEW, PERMISSIONS.FIELD_DELETE])).toBe(true);
    });

    it('should return false when user has none of the permissions', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasAnyPermission(roles, [PERMISSIONS.FIELD_DELETE, PERMISSIONS.SYSTEM_ADMIN])).toBe(false);
    });

    it('should return false for empty required permissions', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasAnyPermission(roles, [])).toBe(false);
    });
  });

  describe('hasAllPermissions', () => {
    it('should return true when user has all permissions', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasAllPermissions(roles, [PERMISSIONS.FIELD_VIEW, PERMISSIONS.NDVI_VIEW])).toBe(true);
    });

    it('should return false when user is missing any permission', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasAllPermissions(roles, [PERMISSIONS.FIELD_VIEW, PERMISSIONS.FIELD_DELETE])).toBe(false);
    });

    it('should return true for empty required permissions', () => {
      const roles: Role[] = [ROLES.FARMER];
      expect(hasAllPermissions(roles, [])).toBe(true);
    });
  });

  describe('getRolePermissions', () => {
    it('should return permissions for farmer role', () => {
      const permissions = getRolePermissions(ROLES.FARMER);
      expect(permissions).toContain(PERMISSIONS.FIELD_VIEW);
      expect(permissions).toContain(PERMISSIONS.NDVI_VIEW);
      expect(permissions).not.toContain(PERMISSIONS.SYSTEM_ADMIN);
    });

    it('should return all permissions for super_admin role', () => {
      const permissions = getRolePermissions(ROLES.SUPER_ADMIN);
      expect(permissions).toContain(PERMISSIONS.SYSTEM_ADMIN);
      expect(permissions).toContain(PERMISSIONS.FIELD_DELETE);
    });

    it('should return empty array for unknown role', () => {
      const permissions = getRolePermissions('unknown_role' as Role);
      expect(permissions).toEqual([]);
    });
  });

  describe('getPermissionsForRoles', () => {
    it('should combine permissions from multiple roles', () => {
      const roles: Role[] = [ROLES.FARMER, ROLES.FIELD_MANAGER];
      const permissions = getPermissionsForRoles(roles);
      expect(permissions).toContain(PERMISSIONS.FIELD_VIEW);
      expect(permissions).toContain(PERMISSIONS.FIELD_CREATE);
    });

    it('should return unique permissions', () => {
      const roles: Role[] = [ROLES.FARMER, ROLES.FARMER];
      const permissions = getPermissionsForRoles(roles);
      const uniqueCount = new Set(permissions).size;
      expect(permissions.length).toBe(uniqueCount);
    });
  });

  describe('ROLE_PERMISSIONS mapping', () => {
    it('should have permissions defined for all roles', () => {
      Object.values(ROLES).forEach((role) => {
        expect(ROLE_PERMISSIONS[role]).toBeDefined();
        expect(Array.isArray(ROLE_PERMISSIONS[role])).toBe(true);
      });
    });

    it('should have super_admin with all permissions', () => {
      const superAdminPermissions = ROLE_PERMISSIONS[ROLES.SUPER_ADMIN];
      const allPermissions = Object.values(PERMISSIONS);
      expect(superAdminPermissions.length).toBe(allPermissions.length);
    });
  });
});
