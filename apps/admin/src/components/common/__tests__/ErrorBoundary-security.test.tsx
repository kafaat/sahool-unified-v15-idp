/**
 * ErrorBoundary Security Tests
 * اختبارات أمان حدود الأخطاء
 *
 * Validates:
 * - Stack traces are hidden in production (no information leakage)
 * - Stack traces are shown in development (for debugging)
 * - Error message is always visible regardless of environment
 * - Sentry event ID is shown in production (for support reference)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import { ErrorBoundary } from "../ErrorBoundary";

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock("../../../lib/logger", () => ({
  logger: {
    log: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    production: vi.fn(),
    critical: vi.fn(),
  },
}));

vi.mock("@sentry/nextjs", () => ({
  captureException: vi.fn(() => "sentry-event-id-abc123"),
}));

// Suppress React error boundary console.error noise in tests
const originalConsoleError = console.error;
beforeEach(() => {
  console.error = vi.fn();
});
afterEach(() => {
  console.error = originalConsoleError;
});

// ═══════════════════════════════════════════════════════════════════════════
// Test component that throws an error
// ═══════════════════════════════════════════════════════════════════════════

function ThrowError({ error }: { error: Error }) {
  throw error;
}

// ═══════════════════════════════════════════════════════════════════════════
// Stack Trace Visibility Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("ErrorBoundary - stack trace security", () => {
  const originalNodeEnv = process.env.NODE_ENV;

  afterEach(() => {
    // Restore original NODE_ENV
    process.env.NODE_ENV = originalNodeEnv;
  });

  it("hides stack trace details when NODE_ENV is production", () => {
    process.env.NODE_ENV = "production";

    const error = new Error("Something went wrong in production");
    error.stack =
      "Error: Something went wrong in production\n    at ProductionComponent (/app/src/components/Secret.tsx:42:7)\n    at renderWithHooks";

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // Stack trace content should NOT be visible
    expect(
      screen.queryByText(/ProductionComponent/),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Secret\.tsx/),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/renderWithHooks/),
    ).not.toBeInTheDocument();

    // The "Stack Trace" summary/details element should not exist
    expect(
      screen.queryByText("Stack Trace (للمطورين)"),
    ).not.toBeInTheDocument();
  });

  it("shows stack trace details when NODE_ENV is development", () => {
    process.env.NODE_ENV = "development";

    const error = new Error("Debug error in development");
    error.stack =
      "Error: Debug error in development\n    at DevComponent (/app/src/components/Debug.tsx:15:3)\n    at renderWithHooks";

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // The "Stack Trace" summary should be present in development
    expect(
      screen.getByText("Stack Trace (للمطورين)"),
    ).toBeInTheDocument();
  });

  it("hides component stack when NODE_ENV is production", () => {
    process.env.NODE_ENV = "production";

    const error = new Error("Production component stack test");
    error.stack = "Error: Production component stack test\n    at SomeComponent";

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // "Component Stack" summary should not appear in production
    expect(
      screen.queryByText("Component Stack"),
    ).not.toBeInTheDocument();
  });

  it("shows component stack when NODE_ENV is development", () => {
    process.env.NODE_ENV = "development";

    const error = new Error("Development component stack test");
    error.stack =
      "Error: Development component stack test\n    at DevComponent";

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // Component Stack summary should be present in development
    // (rendered by componentDidCatch setting errorInfo with componentStack)
    // Note: The component stack is only shown if errorInfo.componentStack is set,
    // which happens via React's componentDidCatch in real rendering.
    // In the test environment, React does provide componentStack.
    expect(
      screen.getByText("Component Stack"),
    ).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Error Message Visibility Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("ErrorBoundary - error message visibility", () => {
  const originalNodeEnv = process.env.NODE_ENV;

  afterEach(() => {
    process.env.NODE_ENV = originalNodeEnv;
  });

  it("always shows error message in production", () => {
    process.env.NODE_ENV = "production";

    const error = new Error("User-facing error message");

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // Error message should always be visible
    expect(
      screen.getByText("User-facing error message"),
    ).toBeInTheDocument();

    // The Arabic error heading should be visible
    expect(
      screen.getByText("خطأ في لوحة التحكم"),
    ).toBeInTheDocument();

    // The Arabic description should be visible
    expect(
      screen.getByText("حدث خطأ غير متوقع أثناء تحميل هذا المكون"),
    ).toBeInTheDocument();
  });

  it("always shows error message in development", () => {
    process.env.NODE_ENV = "development";

    const error = new Error("Development error message");

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // Error message should be visible
    expect(
      screen.getByText("Development error message"),
    ).toBeInTheDocument();
  });

  it("shows error heading regardless of environment", () => {
    process.env.NODE_ENV = "production";

    const error = new Error("Any error");

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // Arabic heading "خطأ في لوحة التحكم" should always be present
    expect(
      screen.getByText("خطأ في لوحة التحكم"),
    ).toBeInTheDocument();

    // Arabic error label "رسالة الخطأ:" should be present
    expect(
      screen.getByText("رسالة الخطأ:"),
    ).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Sentry Event ID Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("ErrorBoundary - Sentry event ID in production", () => {
  const originalNodeEnv = process.env.NODE_ENV;

  afterEach(() => {
    process.env.NODE_ENV = originalNodeEnv;
  });

  it("shows Sentry event ID for support reference after error reporting", async () => {
    process.env.NODE_ENV = "production";

    const error = new Error("Error that gets reported to Sentry");

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // The Sentry event ID should eventually appear (after async import resolves)
    // The Arabic support reference text should be present once eventId is set
    // Note: Since Sentry is dynamically imported, we need to wait for the promise
    const supportText = await screen.findByText(
      "معرف الخطأ للدعم الفني:",
      {},
      { timeout: 3000 },
    );
    expect(supportText).toBeInTheDocument();

    // The event ID value should be shown
    const eventIdElement = await screen.findByText(
      "sentry-event-id-abc123",
      {},
      { timeout: 3000 },
    );
    expect(eventIdElement).toBeInTheDocument();
  });

  it("Sentry event ID is selectable for copy-paste (select-all class)", async () => {
    process.env.NODE_ENV = "production";

    const error = new Error("Sentry ID copy test");

    render(
      <ErrorBoundary>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    // Wait for async Sentry reporting to complete
    const eventIdElement = await screen.findByText(
      "sentry-event-id-abc123",
      {},
      { timeout: 3000 },
    );

    // The event ID code element should have the select-all class for easy copying
    expect(eventIdElement).toHaveClass("select-all");
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Fallback and Retry Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("ErrorBoundary - fallback and retry", () => {
  it("renders custom fallback when provided", () => {
    const error = new Error("Fallback test");

    render(
      <ErrorBoundary fallback={<div data-testid="custom-fallback">Custom Error UI</div>}>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    expect(screen.getByTestId("custom-fallback")).toBeInTheDocument();
    expect(screen.getByText("Custom Error UI")).toBeInTheDocument();

    // Default error UI should NOT be present when fallback is used
    expect(
      screen.queryByText("خطأ في لوحة التحكم"),
    ).not.toBeInTheDocument();
  });

  it("renders children normally when no error occurs", () => {
    render(
      <ErrorBoundary>
        <div data-testid="healthy-child">Healthy content</div>
      </ErrorBoundary>,
    );

    expect(screen.getByTestId("healthy-child")).toBeInTheDocument();
    expect(screen.getByText("Healthy content")).toBeInTheDocument();
  });

  it("calls onError callback when error occurs", () => {
    const onError = vi.fn();
    const error = new Error("Callback test error");

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError error={error} />
      </ErrorBoundary>,
    );

    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError).toHaveBeenCalledWith(
      error,
      expect.objectContaining({
        componentStack: expect.any(String),
      }),
    );
  });
});
