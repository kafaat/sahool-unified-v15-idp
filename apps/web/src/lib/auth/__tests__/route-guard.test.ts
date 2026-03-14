/**
 * Route Guard Tests
 * اختبارات حماية المسارات
 *
 * Tests the checkAccess function from route-guard.tsx
 */
import { describe, it, expect, vi } from "vitest";

// Mock next/navigation and next/headers since route-guard.tsx imports them at module level
vi.mock("next/navigation", () => ({
  redirect: vi.fn(),
}));

vi.mock("next/headers", () => ({
  cookies: vi.fn(),
}));

vi.mock("@/lib/logger", () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}));

import { checkAccess } from "../route-guard";
import type { User, RouteGuardOptions } from "../route-guard";

const makeUser = (overrides: Partial<User> = {}): User => ({
  id: "user-1",
  roles: ["farmer"],
  permissions: ["field:view", "field:edit"],
  tenantId: "tenant-1",
  ...overrides,
});

describe("checkAccess", () => {
  // ═══════════════════════════════════════════════════════════════════════════
  // NULL USER
  // ═══════════════════════════════════════════════════════════════════════════

  describe("null user", () => {
    it("should deny access for null user", () => {
      expect(checkAccess(null, {})).toBe(false);
    });

    it("should deny access for null user with permissions", () => {
      expect(checkAccess(null, { permission: "field:view" })).toBe(false);
    });

    it("should deny access for null user with roles", () => {
      expect(checkAccess(null, { role: "admin" })).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NO REQUIREMENTS
  // ═══════════════════════════════════════════════════════════════════════════

  describe("no requirements", () => {
    it("should grant access when no permission or role is required", () => {
      expect(checkAccess(makeUser(), {})).toBe(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SINGLE PERMISSION
  // ═══════════════════════════════════════════════════════════════════════════

  describe("single permission", () => {
    it("should grant access when user has the required permission", () => {
      const user = makeUser({ permissions: ["field:view", "field:edit"] });
      expect(checkAccess(user, { permission: "field:view" })).toBe(true);
    });

    it("should deny access when user lacks the required permission", () => {
      const user = makeUser({ permissions: ["field:view"] });
      expect(checkAccess(user, { permission: "field:delete" })).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MULTIPLE PERMISSIONS (ANY)
  // ═══════════════════════════════════════════════════════════════════════════

  describe("multiple permissions (any - default)", () => {
    it("should grant access when user has at least one permission", () => {
      const user = makeUser({ permissions: ["field:view"] });
      expect(checkAccess(user, { permission: ["field:view", "field:edit"] })).toBe(true);
    });

    it("should deny access when user has none of the permissions", () => {
      const user = makeUser({ permissions: ["other:view"] });
      expect(checkAccess(user, { permission: ["field:view", "field:edit"] })).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MULTIPLE PERMISSIONS (ALL)
  // ═══════════════════════════════════════════════════════════════════════════

  describe("multiple permissions (all)", () => {
    it("should grant access when user has all permissions", () => {
      const user = makeUser({ permissions: ["field:view", "field:edit", "field:delete"] });
      expect(
        checkAccess(user, {
          permission: ["field:view", "field:edit"],
          requireAll: true,
        }),
      ).toBe(true);
    });

    it("should deny access when user is missing one permission", () => {
      const user = makeUser({ permissions: ["field:view"] });
      expect(
        checkAccess(user, {
          permission: ["field:view", "field:edit"],
          requireAll: true,
        }),
      ).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SINGLE ROLE
  // ═══════════════════════════════════════════════════════════════════════════

  describe("single role", () => {
    it("should grant access when user has the required role", () => {
      const user = makeUser({ roles: ["admin"] });
      expect(checkAccess(user, { role: "admin" })).toBe(true);
    });

    it("should deny access when user lacks the required role", () => {
      const user = makeUser({ roles: ["farmer"] });
      expect(checkAccess(user, { role: "admin" })).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MULTIPLE ROLES (ANY)
  // ═══════════════════════════════════════════════════════════════════════════

  describe("multiple roles (any - default)", () => {
    it("should grant access when user has at least one role", () => {
      const user = makeUser({ roles: ["admin"] });
      expect(checkAccess(user, { role: ["admin", "super_admin"] })).toBe(true);
    });

    it("should deny access when user has none of the roles", () => {
      const user = makeUser({ roles: ["farmer"] });
      expect(checkAccess(user, { role: ["admin", "super_admin"] })).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MULTIPLE ROLES (ALL)
  // ═══════════════════════════════════════════════════════════════════════════

  describe("multiple roles (all)", () => {
    it("should grant access when user has all roles", () => {
      const user = makeUser({ roles: ["admin", "super_admin"] });
      expect(
        checkAccess(user, {
          role: ["admin", "super_admin"],
          requireAll: true,
        }),
      ).toBe(true);
    });

    it("should deny access when user is missing one role", () => {
      const user = makeUser({ roles: ["admin"] });
      expect(
        checkAccess(user, {
          role: ["admin", "super_admin"],
          requireAll: true,
        }),
      ).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // COMBINED PERMISSION + ROLE
  // ═══════════════════════════════════════════════════════════════════════════

  describe("combined permission and role", () => {
    it("should require both permission and role", () => {
      const user = makeUser({
        roles: ["admin"],
        permissions: ["field:view"],
      });
      expect(checkAccess(user, { permission: "field:view", role: "admin" })).toBe(true);
    });

    it("should deny if permission matches but role doesn't", () => {
      const user = makeUser({
        roles: ["farmer"],
        permissions: ["field:view"],
      });
      expect(checkAccess(user, { permission: "field:view", role: "admin" })).toBe(false);
    });

    it("should deny if role matches but permission doesn't", () => {
      const user = makeUser({
        roles: ["admin"],
        permissions: [],
      });
      expect(checkAccess(user, { permission: "field:view", role: "admin" })).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EDGE CASES
  // ═══════════════════════════════════════════════════════════════════════════

  describe("edge cases", () => {
    it("should handle user with empty permissions and roles", () => {
      const user = makeUser({ roles: [], permissions: [] });
      expect(checkAccess(user, {})).toBe(true); // No requirements
      expect(checkAccess(user, { permission: "any" })).toBe(false);
      expect(checkAccess(user, { role: "any" })).toBe(false);
    });

    it("should handle requireAll with single permission", () => {
      const user = makeUser({ permissions: ["field:view"] });
      expect(
        checkAccess(user, { permission: "field:view", requireAll: true }),
      ).toBe(true);
    });

    it("should handle requireAll with single role", () => {
      const user = makeUser({ roles: ["admin"] });
      expect(checkAccess(user, { role: "admin", requireAll: true })).toBe(true);
    });
  });
});
