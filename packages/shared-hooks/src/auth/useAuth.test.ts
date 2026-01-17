import { describe, it, expect, vi } from "vitest";
import { createAuthContextValue } from "./useAuth";
import type { User } from "./useAuth";
import { ROLES, PERMISSIONS } from "./permissions";

// Mock user data
const mockFarmerUser: User = {
  id: "user-123",
  email: "farmer@sahool.sa",
  name: "أحمد المزارع",
  roles: [ROLES.FARMER],
  tenantId: "tenant-456",
};

const mockAdminUser: User = {
  id: "admin-123",
  email: "admin@sahool.sa",
  name: "مدير النظام",
  roles: [ROLES.ADMIN],
  tenantId: "tenant-456",
};

const mockSuperAdminUser: User = {
  id: "superadmin-123",
  email: "superadmin@sahool.sa",
  name: "المدير العام",
  roles: [ROLES.SUPER_ADMIN],
  tenantId: "tenant-456",
};

const mockMultiRoleUser: User = {
  id: "multi-123",
  email: "multi@sahool.sa",
  name: "مستخدم متعدد الأدوار",
  roles: [ROLES.FARMER, ROLES.FIELD_MANAGER],
  tenantId: "tenant-456",
};

// Mock actions
const mockActions = {
  login: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
};

describe("createAuthContextValue", () => {
  describe("with authenticated user", () => {
    it("should return correct auth state for farmer", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(context.user).toEqual(mockFarmerUser);
      expect(context.isAuthenticated).toBe(true);
      expect(context.isLoading).toBe(false);
      expect(context.error).toBeNull();
    });

    it("should return correct auth state for admin", () => {
      const context = createAuthContextValue(
        mockAdminUser,
        false,
        null,
        mockActions,
      );

      expect(context.user).toEqual(mockAdminUser);
      expect(context.isAuthenticated).toBe(true);
    });
  });

  describe("with no user (unauthenticated)", () => {
    it("should return unauthenticated state", () => {
      const context = createAuthContextValue(null, false, null, mockActions);

      expect(context.user).toBeNull();
      expect(context.isAuthenticated).toBe(false);
      expect(context.permissions).toEqual([]);
    });

    it("should return loading state", () => {
      const context = createAuthContextValue(null, true, null, mockActions);

      expect(context.isLoading).toBe(true);
      expect(context.isAuthenticated).toBe(false);
    });

    it("should return error state", () => {
      const error = new Error("Auth failed");
      const context = createAuthContextValue(null, false, error, mockActions);

      expect(context.error).toBe(error);
      expect(context.isAuthenticated).toBe(false);
    });
  });

  describe("permission checks", () => {
    it("farmer should have basic view permissions", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(context.can(PERMISSIONS.FIELD_VIEW)).toBe(true);
      expect(context.can(PERMISSIONS.NDVI_VIEW)).toBe(true);
      expect(context.can(PERMISSIONS.ALERT_VIEW)).toBe(true);
    });

    it("farmer should not have admin permissions", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(context.can(PERMISSIONS.FIELD_DELETE)).toBe(false);
      expect(context.can(PERMISSIONS.SYSTEM_ADMIN)).toBe(false);
      expect(context.can(PERMISSIONS.USER_DELETE)).toBe(false);
    });

    it("admin should have most permissions", () => {
      const context = createAuthContextValue(
        mockAdminUser,
        false,
        null,
        mockActions,
      );

      expect(context.can(PERMISSIONS.FIELD_VIEW)).toBe(true);
      expect(context.can(PERMISSIONS.FIELD_DELETE)).toBe(true);
      expect(context.can(PERMISSIONS.USER_VIEW)).toBe(true);
    });

    it("super_admin should have all permissions", () => {
      const context = createAuthContextValue(
        mockSuperAdminUser,
        false,
        null,
        mockActions,
      );

      expect(context.can(PERMISSIONS.SYSTEM_ADMIN)).toBe(true);
      expect(context.can(PERMISSIONS.FIELD_DELETE)).toBe(true);
      expect(context.can(PERMISSIONS.USER_DELETE)).toBe(true);
    });
  });

  describe("canAny", () => {
    it("should return true if user has any of the permissions", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(
        context.canAny([PERMISSIONS.FIELD_VIEW, PERMISSIONS.SYSTEM_ADMIN]),
      ).toBe(true);
    });

    it("should return false if user has none of the permissions", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(
        context.canAny([PERMISSIONS.FIELD_DELETE, PERMISSIONS.SYSTEM_ADMIN]),
      ).toBe(false);
    });
  });

  describe("canAll", () => {
    it("should return true if user has all permissions", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(
        context.canAll([PERMISSIONS.FIELD_VIEW, PERMISSIONS.NDVI_VIEW]),
      ).toBe(true);
    });

    it("should return false if user lacks any permission", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(
        context.canAll([PERMISSIONS.FIELD_VIEW, PERMISSIONS.FIELD_DELETE]),
      ).toBe(false);
    });
  });

  describe("role checks", () => {
    it("should correctly check hasRole", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(context.hasRole(ROLES.FARMER)).toBe(true);
      expect(context.hasRole(ROLES.ADMIN)).toBe(false);
    });

    it("should correctly check hasAnyRole", () => {
      const context = createAuthContextValue(
        mockMultiRoleUser,
        false,
        null,
        mockActions,
      );

      expect(context.hasAnyRole([ROLES.FARMER, ROLES.ADMIN])).toBe(true);
      expect(context.hasAnyRole([ROLES.ADMIN, ROLES.SUPER_ADMIN])).toBe(false);
    });
  });

  describe("permissions list", () => {
    it("should return permissions array for user roles", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(context.permissions).toContain(PERMISSIONS.FIELD_VIEW);
      expect(context.permissions).toContain(PERMISSIONS.NDVI_VIEW);
      expect(context.permissions).not.toContain(PERMISSIONS.SYSTEM_ADMIN);
    });

    it("should return combined permissions for multi-role user", () => {
      const context = createAuthContextValue(
        mockMultiRoleUser,
        false,
        null,
        mockActions,
      );

      // Should have farmer permissions
      expect(context.permissions).toContain(PERMISSIONS.FIELD_VIEW);
      // Should have field_manager permissions
      expect(context.permissions).toContain(PERMISSIONS.FIELD_CREATE);
      expect(context.permissions).toContain(PERMISSIONS.REPORT_CREATE);
    });

    it("should return empty array for unauthenticated user", () => {
      const context = createAuthContextValue(null, false, null, mockActions);

      expect(context.permissions).toEqual([]);
    });
  });

  describe("actions", () => {
    it("should include login, logout, refreshToken actions", () => {
      const context = createAuthContextValue(
        mockFarmerUser,
        false,
        null,
        mockActions,
      );

      expect(context.login).toBe(mockActions.login);
      expect(context.logout).toBe(mockActions.logout);
      expect(context.refreshToken).toBe(mockActions.refreshToken);
    });
  });
});
