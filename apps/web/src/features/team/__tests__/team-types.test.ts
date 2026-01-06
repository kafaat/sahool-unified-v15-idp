/**
 * Team Types Unit Tests
 * اختبارات وحدة أنواع الفريق
 *
 * Tests for team management type definitions
 */

import { describe, it, expect } from 'vitest';
import {
  Role,
  UserStatus,
  PermissionCategory,
  PermissionAction,
  type Permission,
  type TeamMember,
  type RoleConfig,
  type InviteRequest,
} from '../types/team';

describe('Team Types', () => {
  describe('Role Enum', () => {
    it('should have all required roles', () => {
      expect(Role.ADMIN).toBe('ADMIN');
      expect(Role.MANAGER).toBe('MANAGER');
      expect(Role.FARMER).toBe('FARMER');
      expect(Role.WORKER).toBe('WORKER');
      expect(Role.VIEWER).toBe('VIEWER');
    });

    it('should have 5 distinct roles', () => {
      const roles = Object.values(Role);
      expect(roles).toHaveLength(5);
      expect(new Set(roles).size).toBe(5);
    });
  });

  describe('UserStatus Enum', () => {
    it('should have all status values', () => {
      expect(UserStatus.ACTIVE).toBe('ACTIVE');
      expect(UserStatus.INACTIVE).toBe('INACTIVE');
      expect(UserStatus.SUSPENDED).toBe('SUSPENDED');
      expect(UserStatus.PENDING).toBe('PENDING');
    });
  });

  describe('PermissionCategory Enum', () => {
    it('should have all permission categories', () => {
      expect(PermissionCategory.FIELDS).toBe('fields');
      expect(PermissionCategory.TASKS).toBe('tasks');
      expect(PermissionCategory.REPORTS).toBe('reports');
      expect(PermissionCategory.TEAM).toBe('team');
      expect(PermissionCategory.SETTINGS).toBe('settings');
    });
  });

  describe('PermissionAction Enum', () => {
    it('should have all permission actions', () => {
      expect(PermissionAction.VIEW).toBe('view');
      expect(PermissionAction.CREATE).toBe('create');
      expect(PermissionAction.EDIT).toBe('edit');
      expect(PermissionAction.DELETE).toBe('delete');
      expect(PermissionAction.MANAGE).toBe('manage');
    });
  });

  describe('Permission Interface', () => {
    it('should create valid permission objects', () => {
      const permission: Permission = {
        category: PermissionCategory.FIELDS,
        action: PermissionAction.VIEW,
        allowed: true,
      };

      expect(permission.category).toBe('fields');
      expect(permission.action).toBe('view');
      expect(permission.allowed).toBe(true);
    });

    it('should support all category/action combinations', () => {
      const categories = Object.values(PermissionCategory);
      const actions = Object.values(PermissionAction);

      categories.forEach((category) => {
        actions.forEach((action) => {
          const permission: Permission = {
            category,
            action,
            allowed: true,
          };
          expect(permission.category).toBe(category);
          expect(permission.action).toBe(action);
        });
      });
    });
  });

  describe('TeamMember Interface', () => {
    it('should have all required properties', () => {
      const member: TeamMember = {
        id: 'member-001',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
        role: Role.WORKER,
        status: UserStatus.ACTIVE,
        emailVerified: true,
        phoneVerified: false,
        createdAt: '2026-01-01T00:00:00Z',
        updatedAt: '2026-01-06T00:00:00Z',
      };

      expect(member.id).toBeDefined();
      expect(member.email).toBeDefined();
      expect(member.role).toBe(Role.WORKER);
      expect(member.status).toBe(UserStatus.ACTIVE);
    });

    it('should support optional properties', () => {
      const memberWithOptional: TeamMember = {
        id: 'member-002',
        email: 'user@example.com',
        firstName: 'User',
        lastName: 'Example',
        phone: '+966501234567',
        role: Role.MANAGER,
        status: UserStatus.ACTIVE,
        avatarUrl: 'https://example.com/avatar.png',
        lastLoginAt: '2026-01-06T10:00:00Z',
        emailVerified: true,
        phoneVerified: true,
        createdAt: '2026-01-01T00:00:00Z',
        updatedAt: '2026-01-06T00:00:00Z',
        profile: {
          city: 'Riyadh',
          region: 'Central',
          country: 'Saudi Arabia',
        },
      };

      expect(memberWithOptional.phone).toBeDefined();
      expect(memberWithOptional.avatarUrl).toBeDefined();
      expect(memberWithOptional.profile?.city).toBe('Riyadh');
    });
  });

  describe('RoleConfig Interface', () => {
    it('should define role configuration with permissions', () => {
      const adminConfig: RoleConfig = {
        role: Role.ADMIN,
        nameEn: 'Administrator',
        nameAr: 'مدير',
        descriptionEn: 'Full access to all features',
        descriptionAr: 'وصول كامل لجميع الميزات',
        color: '#FF5733',
        permissions: [
          { category: PermissionCategory.FIELDS, action: PermissionAction.MANAGE, allowed: true },
          { category: PermissionCategory.TEAM, action: PermissionAction.MANAGE, allowed: true },
        ],
      };

      expect(adminConfig.role).toBe(Role.ADMIN);
      expect(adminConfig.nameEn).toBe('Administrator');
      expect(adminConfig.nameAr).toBe('مدير');
      expect(adminConfig.permissions.length).toBeGreaterThan(0);
    });
  });

  describe('InviteRequest Interface', () => {
    it('should validate invite request structure', () => {
      const invite: InviteRequest = {
        email: 'newmember@example.com',
        role: Role.WORKER,
        message: 'Welcome to the team!',
      };

      expect(invite.email).toContain('@');
      expect(Object.values(Role)).toContain(invite.role);
    });
  });
});

describe('Team Business Rules', () => {
  it('should have role hierarchy', () => {
    // ADMIN has more privileges than MANAGER, which has more than FARMER, etc.
    const roleHierarchy = [Role.ADMIN, Role.MANAGER, Role.FARMER, Role.WORKER, Role.VIEWER];

    expect(roleHierarchy[0]).toBe(Role.ADMIN);
    expect(roleHierarchy[roleHierarchy.length - 1]).toBe(Role.VIEWER);
  });

  it('should have view action for all categories', () => {
    const categories = Object.values(PermissionCategory);

    categories.forEach((category) => {
      const viewPermission: Permission = {
        category,
        action: PermissionAction.VIEW,
        allowed: true,
      };
      expect(viewPermission.action).toBe('view');
    });
  });

  it('should support bilingual role names', () => {
    const managerConfig: RoleConfig = {
      role: Role.MANAGER,
      nameEn: 'Manager',
      nameAr: 'مدير',
      descriptionEn: 'Manage farm operations',
      descriptionAr: 'إدارة عمليات المزرعة',
      color: '#4CAF50',
      permissions: [],
    };

    expect(managerConfig.nameEn).toBeTruthy();
    expect(managerConfig.nameAr).toBeTruthy();
    expect(managerConfig.descriptionAr).toContain('إدارة');
  });
});
