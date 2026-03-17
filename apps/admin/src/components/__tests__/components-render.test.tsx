/**
 * Admin Component Render Tests
 * اختبارات عرض مكونات الإدارة
 *
 * Verifies that key admin components render without crashing
 * and display expected content.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

// Mock logger
vi.mock("../../lib/logger", () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    critical: vi.fn(),
    debug: vi.fn(),
  },
}));

// Mock Sentry (dynamically imported by ErrorBoundary)
vi.mock("@sentry/nextjs", () => ({
  captureException: vi.fn().mockReturnValue("mock-event-id"),
}));

// Mock theme store for ThemeToggle
vi.mock("../../stores/theme.store", () => ({
  useTheme: () => ({
    theme: "light",
    resolvedTheme: "light",
    setTheme: vi.fn(),
    toggleTheme: vi.fn(),
  }),
}));

// Mock lib/utils
vi.mock("../../lib/utils", () => ({
  cn: (...args: unknown[]) => args.filter(Boolean).join(" "),
}));

// ---------------------------------------------------------------------------
// Imports
// ---------------------------------------------------------------------------

import { ErrorBoundary } from "../common/ErrorBoundary";
import ThemeToggle from "../ui/ThemeToggle";

// ---------------------------------------------------------------------------
// ErrorBoundary Tests
// ---------------------------------------------------------------------------

describe("Admin ErrorBoundary", () => {
  it("renders children when no error occurs", () => {
    render(
      <ErrorBoundary>
        <div data-testid="child">Normal content</div>
      </ErrorBoundary>,
    );
    expect(screen.getByTestId("child")).toBeInTheDocument();
    expect(screen.getByText("Normal content")).toBeInTheDocument();
  });

  it("renders custom fallback when provided and error occurs", () => {
    const ThrowingComponent = () => {
      throw new Error("Test error");
    };

    // Suppress React error boundary console error
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Custom fallback</div>}>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Custom fallback")).toBeInTheDocument();
    consoleSpy.mockRestore();
  });

  it("renders default error UI when child component throws", () => {
    const ThrowingComponent = () => {
      throw new Error("Something went wrong");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    // Default UI shows Arabic error heading
    expect(screen.getByText("خطأ في لوحة التحكم")).toBeInTheDocument();
    expect(
      screen.getByText("حدث خطأ غير متوقع أثناء تحميل هذا المكون"),
    ).toBeInTheDocument();
    // Retry button should be present
    expect(screen.getByText("إعادة المحاولة")).toBeInTheDocument();
    // Refresh button should be present
    expect(screen.getByText("تحديث الصفحة")).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it("calls onError callback when error occurs", () => {
    const onErrorMock = vi.fn();
    const ThrowingComponent = () => {
      throw new Error("Callback test");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary onError={onErrorMock}>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    expect(onErrorMock).toHaveBeenCalledTimes(1);
    expect(onErrorMock).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      }),
    );

    consoleSpy.mockRestore();
  });

  it("displays error message in the error detail box", () => {
    const ThrowingComponent = () => {
      throw new Error("Specific error message");
    };

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    );

    expect(screen.getByText("رسالة الخطأ:")).toBeInTheDocument();
    expect(screen.getByText("Specific error message")).toBeInTheDocument();

    consoleSpy.mockRestore();
  });
});

// ---------------------------------------------------------------------------
// ThemeToggle Tests
// ---------------------------------------------------------------------------

describe("Admin ThemeToggle", () => {
  it("renders icon variant without crashing", () => {
    render(<ThemeToggle />);
    // Default variant is "icon", should render a button with aria-label
    const button = screen.getByRole("button", {
      name: /تبديل للوضع الداكن/i,
    });
    expect(button).toBeInTheDocument();
  });

  it("renders button variant with text", () => {
    render(<ThemeToggle variant="button" />);
    const button = screen.getByRole("button", {
      name: /تبديل للوضع الداكن/i,
    });
    expect(button).toBeInTheDocument();
    expect(screen.getByText("الوضع الداكن")).toBeInTheDocument();
  });

  it("renders dropdown variant", () => {
    render(<ThemeToggle variant="dropdown" />);
    const button = screen.getByRole("button", { name: /اختيار السمة/i });
    expect(button).toBeInTheDocument();
  });
});
