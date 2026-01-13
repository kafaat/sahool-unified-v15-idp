/**
 * PermissionGate Component Tests
 * اختبارات مكون بوابة الصلاحيات
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PermissionGate, RoleGate, AdminGate } from "./PermissionGate";

// Mock auth context value
const createMockAuth = (
  overrides: Partial<{
    can: (permission: string) => boolean;
    canAny: (permissions: string[]) => boolean;
    canAll: (permissions: string[]) => boolean;
    hasRole: (role: string) => boolean;
    hasAnyRole: (roles: string[]) => boolean;
  }> = {},
) => ({
  can: (permission: string) => false,
  canAny: (permissions: string[]) => false,
  canAll: (permissions: string[]) => false,
  hasRole: (role: string) => false,
  hasAnyRole: (roles: string[]) => false,
  ...overrides,
});

describe("PermissionGate", () => {
  describe("when user has required permission", () => {
    const mockAuth = createMockAuth({
      can: (p) => p === "field:view",
      canAny: (ps) => ps.some((p) => p === "field:view"),
      canAll: (ps) => ps.every((p) => p === "field:view"),
    });

    it("should render children", () => {
      render(
        <PermissionGate permission="field:view" auth={mockAuth}>
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>,
      );

      expect(screen.getByTestId("protected-content")).toBeInTheDocument();
      expect(screen.getByText("المحتوى المحمي")).toBeInTheDocument();
    });

    it("should not render fallback", () => {
      render(
        <PermissionGate
          permission="field:view"
          fallback={<div data-testid="fallback">غير مصرح</div>}
          auth={mockAuth}
        >
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>,
      );

      expect(screen.queryByTestId("fallback")).not.toBeInTheDocument();
    });
  });

  describe("when user lacks required permission", () => {
    const mockAuth = createMockAuth({
      can: () => false,
      canAny: () => false,
      canAll: () => false,
    });

    it("should not render children", () => {
      render(
        <PermissionGate permission="admin:users" auth={mockAuth}>
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>,
      );

      expect(screen.queryByTestId("protected-content")).not.toBeInTheDocument();
    });

    it("should render fallback when provided", () => {
      render(
        <PermissionGate
          permission="admin:users"
          fallback={<div data-testid="fallback">غير مصرح</div>}
          auth={mockAuth}
        >
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>,
      );

      expect(screen.getByTestId("fallback")).toBeInTheDocument();
      expect(screen.getByText("غير مصرح")).toBeInTheDocument();
    });
  });

  describe("with no permission or role specified", () => {
    const mockAuth = createMockAuth();

    it("should render children (allow by default)", () => {
      render(
        <PermissionGate auth={mockAuth}>
          <div data-testid="content">محتوى عام</div>
        </PermissionGate>,
      );

      expect(screen.getByTestId("content")).toBeInTheDocument();
    });
  });

  describe("with multiple permissions (requireAll=false)", () => {
    const mockAuth = createMockAuth({
      canAny: (ps) => ps.includes("field:view"),
    });

    it("should render when user has any of the permissions", () => {
      render(
        <PermissionGate
          permission={["field:view", "field:edit"]}
          auth={mockAuth}
        >
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>,
      );

      expect(screen.getByTestId("protected-content")).toBeInTheDocument();
    });
  });

  describe("with multiple permissions (requireAll=true)", () => {
    const mockAuth = createMockAuth({
      canAll: (ps) => ps.length === 1 && ps[0] === "field:view",
    });

    it("should not render when user lacks any permission", () => {
      render(
        <PermissionGate
          permission={["field:view", "field:edit"]}
          requireAll
          auth={mockAuth}
        >
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>,
      );

      expect(screen.queryByTestId("protected-content")).not.toBeInTheDocument();
    });
  });
});

describe("RoleGate", () => {
  it("should render children when user has required role", () => {
    const mockAuth = createMockAuth({
      hasRole: (r) => r === "agronomist",
      hasAnyRole: (rs) => rs.includes("agronomist"),
    });

    render(
      <RoleGate role="agronomist" auth={mockAuth}>
        <div data-testid="role-content">محتوى المهندس الزراعي</div>
      </RoleGate>,
    );

    expect(screen.getByTestId("role-content")).toBeInTheDocument();
  });

  it("should not render when user lacks role", () => {
    const mockAuth = createMockAuth({
      hasRole: () => false,
      hasAnyRole: () => false,
    });

    render(
      <RoleGate role="admin" auth={mockAuth}>
        <div data-testid="role-content">محتوى المدير</div>
      </RoleGate>,
    );

    expect(screen.queryByTestId("role-content")).not.toBeInTheDocument();
  });

  it("should render when user has any of multiple roles", () => {
    const mockAuth = createMockAuth({
      hasAnyRole: (rs) => rs.includes("farmer"),
    });

    render(
      <RoleGate role={["farmer", "agronomist"]} auth={mockAuth}>
        <div data-testid="role-content">محتوى</div>
      </RoleGate>,
    );

    expect(screen.getByTestId("role-content")).toBeInTheDocument();
  });
});

describe("AdminGate", () => {
  it("should render for admin user", () => {
    const mockAuth = createMockAuth({
      hasAnyRole: (rs) => rs.includes("admin"),
    });

    render(
      <AdminGate auth={mockAuth}>
        <div data-testid="admin-content">لوحة التحكم</div>
      </AdminGate>,
    );

    expect(screen.getByTestId("admin-content")).toBeInTheDocument();
  });

  it("should render for super_admin user", () => {
    const mockAuth = createMockAuth({
      hasAnyRole: (rs) => rs.includes("super_admin"),
    });

    render(
      <AdminGate auth={mockAuth}>
        <div data-testid="admin-content">لوحة التحكم</div>
      </AdminGate>,
    );

    expect(screen.getByTestId("admin-content")).toBeInTheDocument();
  });

  it("should not render for non-admin user", () => {
    const mockAuth = createMockAuth({
      hasAnyRole: () => false,
    });

    render(
      <AdminGate auth={mockAuth}>
        <div data-testid="admin-content">لوحة التحكم</div>
      </AdminGate>,
    );

    expect(screen.queryByTestId("admin-content")).not.toBeInTheDocument();
  });
});
