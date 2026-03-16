/**
 * Toast Notification System Tests
 * اختبارات نظام الإشعارات المنبثقة
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import React from "react";

vi.mock("@/lib/utils", () => ({
  cn: (...args: unknown[]) => args.filter(Boolean).join(" "),
}));

vi.mock("lucide-react", () => {
  const _React = require("react");
  const _mk = (name: string) => {
    const C = (props: Record<string, unknown>) =>
      _React.createElement("svg", { "data-testid": `icon-${name}`, ...props });
    C.displayName = name;
    return C;
  };
  return {
    __esModule: true,
    X: _mk("X"),
    CheckCircle2: _mk("CheckCircle2"),
    AlertCircle: _mk("AlertCircle"),
    Info: _mk("Info"),
    AlertTriangle: _mk("AlertTriangle"),
  };
});

import { ToastProvider, useToast } from "../Toast";

// Helper component to trigger toasts
function ToastTrigger() {
  const { toast } = useToast();
  return (
    <div>
      <button onClick={() => toast.success("Done", "تمت العملية")}>
        Success
      </button>
      <button onClick={() => toast.error("Error occurred", "حدث خطأ")}>
        Error
      </button>
      <button onClick={() => toast.warning("Warning", "تحذير")}>
        Warning
      </button>
      <button onClick={() => toast.info("Info", "معلومات")}>Info</button>
    </div>
  );
}

describe("ToastProvider", () => {

  it("renders children", () => {
    render(
      <ToastProvider>
        <span>content</span>
      </ToastProvider>,
    );
    expect(screen.getByText("content")).toBeInTheDocument();
  });

  it("shows success toast", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Success"));
    expect(screen.getByText("تمت العملية")).toBeInTheDocument();
    expect(screen.getByText("Done")).toBeInTheDocument();
  });

  it("shows error toast", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Error"));
    expect(screen.getByText("حدث خطأ")).toBeInTheDocument();
    expect(screen.getByText("Error occurred")).toBeInTheDocument();
  });

  it("shows warning toast", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Warning"));
    expect(screen.getByText("تحذير")).toBeInTheDocument();
  });

  it("shows info toast", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Info"));
    expect(screen.getByText("معلومات")).toBeInTheDocument();
  });

  it("renders toast with role=alert", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Success"));
    const alerts = screen.getAllByRole("alert");
    expect(alerts.length).toBeGreaterThan(0);
  });

  it("renders toast container with aria-label", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    expect(screen.getByLabelText("الإشعارات")).toBeInTheDocument();
  });

  it("has a close button on toasts", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Success"));
    expect(screen.getByText("تمت العملية")).toBeInTheDocument();

    const closeBtn = screen.getByLabelText("إغلاق الإشعار");
    expect(closeBtn).toBeInTheDocument();
    // Click close - starts exit animation
    fireEvent.click(closeBtn);
  });

  it("can show multiple toasts", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Success"));
    fireEvent.click(screen.getByText("Error"));
    fireEvent.click(screen.getByText("Warning"));

    expect(screen.getByText("تمت العملية")).toBeInTheDocument();
    expect(screen.getByText("حدث خطأ")).toBeInTheDocument();
    expect(screen.getByText("تحذير")).toBeInTheDocument();
  });

  it("limits to 5 toasts max", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    // Add 6 toasts
    for (let i = 0; i < 6; i++) {
      fireEvent.click(screen.getByText("Success"));
    }
    const alerts = screen.getAllByRole("alert");
    expect(alerts.length).toBeLessThanOrEqual(5);
  });
});

describe("useToast", () => {
  it("throws when used outside ToastProvider", () => {
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<ToastTrigger />)).toThrow(
      "useToast must be used within ToastProvider",
    );
    consoleSpy.mockRestore();
  });
});
