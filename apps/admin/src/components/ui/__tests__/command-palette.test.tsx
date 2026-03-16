/**
 * CommandPalette Component Tests
 * اختبارات مكون لوحة الأوامر السريعة
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import React from "react";

// ─── Mocks ────────────────────────────────────────────────────────────────────

const mockPush = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => "/dashboard",
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
    Search: _mk("Search"),
    LayoutDashboard: _mk("LayoutDashboard"),
    MapPin: _mk("MapPin"),
    Bug: _mk("Bug"),
    Droplets: _mk("Droplets"),
    Users: _mk("Users"),
    Settings: _mk("Settings"),
    ShoppingCart: _mk("ShoppingCart"),
    Wrench: _mk("Wrench"),
    Package: _mk("Package"),
    CheckSquare: _mk("CheckSquare"),
    Activity: _mk("Activity"),
    Bell: _mk("Bell"),
    TrendingUp: _mk("TrendingUp"),
    Sprout: _mk("Sprout"),
    Satellite: _mk("Satellite"),
    FlaskConical: _mk("FlaskConical"),
    Shield: _mk("Shield"),
    MessageCircle: _mk("MessageCircle"),
    Plane: _mk("Plane"),
    Mountain: _mk("Mountain"),
    Eye: _mk("Eye"),
    Cpu: _mk("Cpu"),
    ClipboardList: _mk("ClipboardList"),
  };
});

vi.mock("@/lib/utils", () => ({
  cn: (...args: unknown[]) => args.filter(Boolean).join(" "),
}));

import CommandPalette from "../CommandPalette";

describe("CommandPalette", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // jsdom doesn't implement scrollIntoView
    Element.prototype.scrollIntoView = vi.fn();
  });

  it("is not visible by default", () => {
    render(<CommandPalette />);
    expect(screen.queryByLabelText("بحث في لوحة الأوامر")).not.toBeInTheDocument();
  });

  it("opens when Ctrl+K is pressed", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });
    expect(screen.getByLabelText("بحث في لوحة الأوامر")).toBeInTheDocument();
  });

  it("opens when Meta+K is pressed", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", metaKey: true });
    expect(screen.getByLabelText("بحث في لوحة الأوامر")).toBeInTheDocument();
  });

  it("closes on Escape key", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });
    expect(screen.getByLabelText("بحث في لوحة الأوامر")).toBeInTheDocument();

    fireEvent.keyDown(screen.getByLabelText("بحث في لوحة الأوامر"), { key: "Escape" });
    expect(screen.queryByLabelText("بحث في لوحة الأوامر")).not.toBeInTheDocument();
  });

  it("closes when backdrop is clicked", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });
    expect(screen.getByLabelText("بحث في لوحة الأوامر")).toBeInTheDocument();

    // Click backdrop
    const backdrop = document.querySelector(".bg-black\\/50");
    if (backdrop) fireEvent.click(backdrop);
    expect(screen.queryByLabelText("بحث في لوحة الأوامر")).not.toBeInTheDocument();
  });

  it("shows all commands when query is empty", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    expect(screen.getByText("لوحة التحكم")).toBeInTheDocument();
    expect(screen.getByText("المزارع")).toBeInTheDocument();
    expect(screen.getByText("الإعدادات")).toBeInTheDocument();
  });

  it("filters commands by Arabic query", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    const input = screen.getByLabelText("بحث في لوحة الأوامر");
    fireEvent.change(input, { target: { value: "الري" } });

    expect(screen.getByText("الري")).toBeInTheDocument();
    // Should not show unrelated items
    expect(screen.queryByText("المستخدمين")).not.toBeInTheDocument();
  });

  it("filters commands by English query", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    const input = screen.getByLabelText("بحث في لوحة الأوامر");
    fireEvent.change(input, { target: { value: "dashboard" } });

    expect(screen.getByText("لوحة التحكم")).toBeInTheDocument();
  });

  it("filters commands by keyword", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    const input = screen.getByLabelText("بحث في لوحة الأوامر");
    fireEvent.change(input, { target: { value: "iot" } });

    expect(screen.getByText("المستشعرات")).toBeInTheDocument();
  });

  it("shows 'no results' for unknown query", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    const input = screen.getByLabelText("بحث في لوحة الأوامر");
    fireEvent.change(input, { target: { value: "xyznonexistent" } });

    expect(screen.getByText(/لا توجد نتائج/)).toBeInTheDocument();
  });

  it("navigates to selected command on Enter", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    const input = screen.getByLabelText("بحث في لوحة الأوامر");
    // First item is Dashboard
    fireEvent.keyDown(input, { key: "Enter" });

    expect(mockPush).toHaveBeenCalledWith("/dashboard");
  });

  it("navigates down with ArrowDown and selects second item", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    const input = screen.getByLabelText("بحث في لوحة الأوامر");
    fireEvent.keyDown(input, { key: "ArrowDown" });
    fireEvent.keyDown(input, { key: "Enter" });

    // Second item is Farms
    expect(mockPush).toHaveBeenCalledWith("/farms");
  });

  it("renders section headers", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    expect(screen.getByText("الرئيسية")).toBeInTheDocument();
    expect(screen.getByText("العمليات")).toBeInTheDocument();
    expect(screen.getByText("المراقبة")).toBeInTheDocument();
    expect(screen.getByText("الإدارة")).toBeInTheDocument();
  });

  it("renders keyboard shortcut hints in footer", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    expect(screen.getByText("للتنقل")).toBeInTheDocument();
    expect(screen.getByText("للفتح")).toBeInTheDocument();
  });

  it("has proper ARIA attributes", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });

    const listbox = screen.getByRole("listbox");
    expect(listbox).toHaveAttribute("aria-label", "نتائج البحث");

    const options = screen.getAllByRole("option");
    expect(options.length).toBeGreaterThan(0);
    expect(options[0]).toHaveAttribute("aria-selected", "true");
  });
});
