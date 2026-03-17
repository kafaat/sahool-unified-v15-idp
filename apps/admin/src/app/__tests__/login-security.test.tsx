/**
 * Login Page Security Tests
 * اختبارات أمان صفحة تسجيل الدخول
 *
 * Validates:
 * - Demo credentials removed from login page
 * - Login form renders correctly
 * - No hardcoded credentials visible
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn().mockResolvedValue(undefined),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/login",
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => React.createElement("a", { href }, children),
}));

vi.mock("@/stores/auth.store", () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn(),
    logout: vi.fn(),
    checkAuth: vi.fn(),
  }),
}));

describe("Login Page Security", () => {
  it("renders login form with email and password fields", async () => {
    const LoginPage = (await import("@/app/(auth)/login/page")).default;
    render(React.createElement(LoginPage));

    expect(screen.getByLabelText("البريد الإلكتروني")).toBeInTheDocument();
    expect(screen.getByLabelText("كلمة المرور")).toBeInTheDocument();
  });

  it("renders login button", async () => {
    const LoginPage = (await import("@/app/(auth)/login/page")).default;
    render(React.createElement(LoginPage));

    expect(
      screen.getByRole("button", { name: /تسجيل الدخول/ }),
    ).toBeInTheDocument();
  });

  it("does NOT display demo credentials", async () => {
    const LoginPage = (await import("@/app/(auth)/login/page")).default;
    render(React.createElement(LoginPage));

    // These were removed for security
    expect(screen.queryByText(/بيانات الدخول للتجربة/)).not.toBeInTheDocument();
    expect(screen.queryByText(/admin123/)).not.toBeInTheDocument();
  });

  it("does NOT contain hardcoded passwords in the page source", async () => {
    // Read the actual source file to verify no credentials
    const fs = await import("fs");
    const path = await import("path");
    const loginPagePath = path.resolve(
      __dirname,
      "../(auth)/login/page.tsx",
    );
    const source = fs.readFileSync(loginPagePath, "utf-8");

    // Should not contain any hardcoded passwords
    expect(source).not.toContain("admin123");
    expect(source).not.toContain("password123");
    expect(source).not.toContain("بيانات الدخول للتجربة");
  });

  it("shows registration link", async () => {
    const LoginPage = (await import("@/app/(auth)/login/page")).default;
    render(React.createElement(LoginPage));

    expect(screen.getByText(/إنشاء حساب جديد/)).toBeInTheDocument();
  });

  it("shows forgot password link", async () => {
    const LoginPage = (await import("@/app/(auth)/login/page")).default;
    render(React.createElement(LoginPage));

    expect(screen.getByText(/نسيت كلمة المرور/)).toBeInTheDocument();
  });
});
