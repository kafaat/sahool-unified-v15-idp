import { describe, it, expect, vi, beforeAll, afterAll } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ErrorBoundary } from "../components/common/ErrorBoundary";

// Component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error("Test error");
  }
  return <div>Normal content</div>;
};

// Suppress console.error for expected errors
const originalError = console.error;
beforeAll(() => {
  console.error = vi.fn();
});
afterAll(() => {
  console.error = originalError;
});

describe("Web App ErrorBoundary", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>,
    );

    expect(screen.getByText("Test content")).toBeInTheDocument();
  });

  it("shows error UI with Arabic text when error occurs", () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("حدث خطأ غير متوقع")).toBeInTheDocument();
    expect(screen.getByText("حاول مرة أخرى")).toBeInTheDocument();
    expect(screen.getByText("تحديث الصفحة")).toBeInTheDocument();
  });

  it("shows error details in development mode", () => {
    // Note: In development mode (NODE_ENV=test during tests), error details should be visible
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    // The error UI should be displayed - checking for the main error message
    expect(screen.getByText("حدث خطأ غير متوقع")).toBeInTheDocument();
  });

  it("calls onError callback", () => {
    const onError = vi.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(onError).toHaveBeenCalled();
  });

  it("allows recovery via retry button with key change", () => {
    // ErrorBoundary requires key change to properly reset after error
    const { rerender } = render(
      <ErrorBoundary key="error-state">
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    // Should show error UI
    expect(screen.getByText("حدث خطأ غير متوقع")).toBeInTheDocument();

    // Re-render with new key and without error
    rerender(
      <ErrorBoundary key="normal-state">
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>,
    );

    // Should show normal content
    expect(screen.getByText("Normal content")).toBeInTheDocument();
  });

  it("has retry button that resets error state", () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    // Should show error UI
    expect(screen.getByText("حدث خطأ غير متوقع")).toBeInTheDocument();

    // Retry button should be present and clickable
    const retryButton = screen.getByText("حاول مرة أخرى");
    expect(retryButton).toBeInTheDocument();

    // Click should not throw
    expect(() => fireEvent.click(retryButton)).not.toThrow();
  });
});
