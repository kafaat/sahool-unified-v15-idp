/**
 * Route Protection Tests
 * اختبارات حماية المسارات
 *
 * Tests route-protection.ts: getRequiredRoles, isPublicRoute,
 * isAdminOnlyRoute, hasRouteAccess, getUnauthorizedRedirect
 */

import { describe, it, expect } from "vitest";
import {
  getRequiredRoles,
  isPublicRoute,
  isAdminOnlyRoute,
  hasRouteAccess,
  getUnauthorizedRedirect,
  PROTECTED_ROUTES,
  PUBLIC_ROUTES,
} from "../route-protection";

describe("PUBLIC_ROUTES", () => {
  it("includes auth pages", () => {
    expect(PUBLIC_ROUTES).toContain("/login");
    expect(PUBLIC_ROUTES).toContain("/register");
    expect(PUBLIC_ROUTES).toContain("/forgot-password");
    expect(PUBLIC_ROUTES).toContain("/reset-password");
    expect(PUBLIC_ROUTES).toContain("/verify-otp");
  });

  it("includes auth API routes", () => {
    expect(PUBLIC_ROUTES).toContain("/api/auth/login");
    expect(PUBLIC_ROUTES).toContain("/api/auth/refresh");
    expect(PUBLIC_ROUTES).toContain("/api/health");
  });
});

describe("PROTECTED_ROUTES", () => {
  it("has admin-only settings route", () => {
    expect(PROTECTED_ROUTES["/settings"]).toEqual(["admin"]);
  });

  it("has admin+supervisor for farms", () => {
    expect(PROTECTED_ROUTES["/farms"]).toEqual(["admin", "supervisor"]);
  });

  it("has all roles for dashboard", () => {
    expect(PROTECTED_ROUTES["/dashboard"]).toEqual([
      "admin",
      "supervisor",
      "viewer",
    ]);
  });
});

describe("isPublicRoute", () => {
  it("returns true for public routes", () => {
    expect(isPublicRoute("/login")).toBe(true);
    expect(isPublicRoute("/api/auth/login")).toBe(true);
    expect(isPublicRoute("/api/health")).toBe(true);
    expect(isPublicRoute("/register")).toBe(true);
  });

  it("returns false for protected routes", () => {
    expect(isPublicRoute("/dashboard")).toBe(false);
    expect(isPublicRoute("/settings")).toBe(false);
    expect(isPublicRoute("/farms")).toBe(false);
  });

  it("matches prefix — /login/callback is public", () => {
    expect(isPublicRoute("/login/callback")).toBe(true);
  });
});

describe("getRequiredRoles", () => {
  it("returns null for public routes", () => {
    expect(getRequiredRoles("/login")).toBeNull();
    expect(getRequiredRoles("/api/auth/login")).toBeNull();
    expect(getRequiredRoles("/api/health")).toBeNull();
  });

  it("returns admin for settings", () => {
    expect(getRequiredRoles("/settings")).toEqual(["admin"]);
  });

  it("returns admin+supervisor for farms", () => {
    expect(getRequiredRoles("/farms")).toEqual(["admin", "supervisor"]);
  });

  it("returns all roles for dashboard", () => {
    expect(getRequiredRoles("/dashboard")).toEqual([
      "admin",
      "supervisor",
      "viewer",
    ]);
  });

  it("matches prefix for sub-routes", () => {
    expect(getRequiredRoles("/settings/security")).toEqual(["admin"]);
  });

  it("returns default roles for unknown routes", () => {
    expect(getRequiredRoles("/some-new-page")).toEqual([
      "admin",
      "supervisor",
      "viewer",
    ]);
  });
});

describe("isAdminOnlyRoute", () => {
  it("returns true for admin-only routes", () => {
    expect(isAdminOnlyRoute("/settings")).toBe(true);
    expect(isAdminOnlyRoute("/api/admin")).toBe(true);
  });

  it("returns false for multi-role routes", () => {
    expect(isAdminOnlyRoute("/farms")).toBe(false);
    expect(isAdminOnlyRoute("/dashboard")).toBe(false);
  });

  it("returns false for public routes", () => {
    expect(isAdminOnlyRoute("/login")).toBe(false);
  });
});

describe("hasRouteAccess", () => {
  it("everyone has access to public routes", () => {
    expect(hasRouteAccess("/login", "viewer")).toBe(true);
    expect(hasRouteAccess("/api/health", "viewer")).toBe(true);
  });

  it("admin has access to everything", () => {
    expect(hasRouteAccess("/settings", "admin")).toBe(true);
    expect(hasRouteAccess("/farms", "admin")).toBe(true);
    expect(hasRouteAccess("/dashboard", "admin")).toBe(true);
  });

  it("supervisor cannot access admin routes", () => {
    expect(hasRouteAccess("/settings", "supervisor")).toBe(false);
    expect(hasRouteAccess("/api/admin", "supervisor")).toBe(false);
  });

  it("supervisor can access supervisor routes", () => {
    expect(hasRouteAccess("/farms", "supervisor")).toBe(true);
    expect(hasRouteAccess("/alerts", "supervisor")).toBe(true);
  });

  it("viewer cannot access admin or supervisor routes", () => {
    expect(hasRouteAccess("/settings", "viewer")).toBe(false);
    expect(hasRouteAccess("/farms", "viewer")).toBe(false);
  });

  it("viewer can access dashboard", () => {
    expect(hasRouteAccess("/dashboard", "viewer")).toBe(true);
    expect(hasRouteAccess("/analytics", "viewer")).toBe(true);
  });
});

describe("getUnauthorizedRedirect", () => {
  it("redirects all roles to dashboard", () => {
    expect(getUnauthorizedRedirect("admin")).toBe("/dashboard");
    expect(getUnauthorizedRedirect("supervisor")).toBe("/dashboard");
    expect(getUnauthorizedRedirect("viewer")).toBe("/dashboard");
  });
});
