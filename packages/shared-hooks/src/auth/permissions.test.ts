import { describe, it, expect } from 'vitest';
import {
  PERMISSIONS,
  ROLES,
  ROLE_PERMISSIONS,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  getRolePermissions,
  isValidPermission,
  isValidRole,
} from './permissions';

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
      expect(PERMISSIONS.ALERT_DISMISS).toBe('alert:dismiss');
    });

    it('should have admin permissions', () => {
      expect(PERMISSIONS.ADMIN_USERS).toBe('admin:users');
      expect(PERMISSIONS.ADMIN_SETTINGS).toBe('admin:settings');
      expect(PERMISSIONS.ADMIN_SYSTEM).toBe('admin:system');
    });
  });

  describe('ROLES constant', () => {
    it('should have all defined roles', () => {
      expect(ROLES.FARMER).toBe('farmer');
      expect(ROLES.AGRONOMIST).toBe('agronomist');
      expect(ROLES.ADMIN).toBe('admin');
      expect(ROLES.SUPER_ADMIN).toBe('super_admin');
    });
  });

  describe('hasPermission', () => {
    const userPermissions = ['field:view', 'field:create', 'ndvi:view'];

    it('should return true when user has the permission', () => {
      expect(hasPermission(userPermissions, 'field:view')).toBe(true);
      expect(hasPermission(userPermissions, 'field:create')).toBe(true);
    });

    it('should return false when user lacks the permission', () => {
      expect(hasPermission(userPermissions, 'field:delete')).toBe(false);
      expect(hasPermission(userPermissions, 'admin:users')).toBe(false);
    });

    it('should return false for empty permissions array', () => {
      expect(hasPermission([], 'field:view')).toBe(false);
    });
  });

  describe('hasAnyPermission', () => {
    const userPermissions = ['field:view', 'ndvi:view'];

    it('should return true when user has any of the permissions', () => {
      expect(hasAnyPermission(userPermissions, ['field:view', 'field:edit'])).toBe(true);
      expect(hasAnyPermission(userPermissions, ['field:delete', 'ndvi:view'])).toBe(true);
    });

    it('should return false when user has none of the permissions', () => {
      expect(hasAnyPermission(userPermissions, ['field:delete', 'admin:users'])).toBe(false);
    });

    it('should return false for empty required permissions', () => {
      expect(hasAnyPermission(userPermissions, [])).toBe(false);
    });
  });

  describe('hasAllPermissions', () => {
    const userPermissions = ['field:view', 'field:create', 'ndvi:view'];

    it('should return true when user has all permissions', () => {
      expect(hasAllPermissions(userPermissions, ['field:view', 'field:create'])).toBe(true);
    });

    it('should return false when user is missing any permission', () => {
      expect(hasAllPermissions(userPermissions, ['field:view', 'field:delete'])).toBe(false);
    });

    it('should return true for empty required permissions', () => {
      expect(hasAllPermissions(userPermissions, [])).toBe(true);
    });
  });

  describe('getRolePermissions', () => {
    it('should return permissions for farmer role', () => {
      const permissions = getRolePermissions('farmer');
      expect(permissions).toContain('field:view');
      expect(permissions).toContain('ndvi:view');
      expect(permissions).not.toContain('admin:users');
    });

    it('should return permissions for admin role', () => {
      const permissions = getRolePermissions('admin');
      expect(permissions).toContain('admin:users');
      expect(permissions).toContain('admin:settings');
    });

    it('should return empty array for unknown role', () => {
      const permissions = getRolePermissions('unknown_role');
      expect(permissions).toEqual([]);
    });
  });

  describe('isValidPermission', () => {
    it('should return true for valid permissions', () => {
      expect(isValidPermission('field:view')).toBe(true);
      expect(isValidPermission('admin:system')).toBe(true);
    });

    it('should return false for invalid permissions', () => {
      expect(isValidPermission('invalid:permission')).toBe(false);
      expect(isValidPermission('')).toBe(false);
    });
  });

  describe('isValidRole', () => {
    it('should return true for valid roles', () => {
      expect(isValidRole('farmer')).toBe(true);
      expect(isValidRole('admin')).toBe(true);
    });

    it('should return false for invalid roles', () => {
      expect(isValidRole('invalid_role')).toBe(false);
      expect(isValidRole('')).toBe(false);
    });
  });
});
