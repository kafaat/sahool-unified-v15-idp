/**
 * Layout Component Tests
 * اختبارات مكونات التخطيط
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";

// Mock next/navigation
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

// Mock next/link
vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
  } & Record<string, unknown>) =>
    React.createElement("a", { href, ...props }, children),
}));

// Mock next/dynamic
vi.mock("next/dynamic", () => ({
  default: () => () => null,
}));

// Mock auth store
vi.mock("@/stores/auth.store", () => ({
  useAuth: () => ({
    user: {
      id: "1",
      email: "admin@sahool.io",
      name: "Admin User",
      name_ar: "مدير النظام",
      role: "admin",
    },
    isAuthenticated: true,
    isLoading: false,
    logout: vi.fn(),
    login: vi.fn(),
    checkAuth: vi.fn(),
  }),
}));

// Mock theme store
vi.mock("@/stores/theme.store", () => ({
  useTheme: () => ({
    theme: "light",
    resolvedTheme: "light",
    setTheme: vi.fn(),
    toggleTheme: vi.fn(),
  }),
}));

// Mock lucide-react icons
vi.mock("lucide-react", () => {
  const createIcon = (name: string) => {
    const Icon = (props: Record<string, unknown>) =>
      React.createElement("svg", { "data-testid": `icon-${name}`, ...props });
    Icon.displayName = name;
    return Icon;
  };
  return {
    LayoutDashboard: createIcon("layout-dashboard"),
    MapPin: createIcon("map-pin"),
    Bug: createIcon("bug"),
    Thermometer: createIcon("thermometer"),
    Settings: createIcon("settings"),
    Bell: createIcon("bell"),
    LogOut: createIcon("log-out"),
    Leaf: createIcon("leaf"),
    MessageCircle: createIcon("message-circle"),
    TrendingUp: createIcon("trending-up"),
    Activity: createIcon("activity"),
    Cpu: createIcon("cpu"),
    Droplets: createIcon("droplets"),
    Sprout: createIcon("sprout"),
    FileText: createIcon("file-text"),
    DollarSign: createIcon("dollar-sign"),
    Satellite: createIcon("satellite"),
    ChevronDown: createIcon("chevron-down"),
    ChevronRight: createIcon("chevron-right"),
    CircleDot: createIcon("circle-dot"),
    Menu: createIcon("menu"),
    Users: createIcon("users"),
    Package: createIcon("package"),
    CheckSquare: createIcon("check-square"),
    Wrench: createIcon("wrench"),
    ShoppingCart: createIcon("shopping-cart"),
    FlaskConical: createIcon("flask-conical"),
    Moon: createIcon("moon"),
    Sun: createIcon("sun"),
    Search: createIcon("search"),
    X: createIcon("x"),
    Loader2: createIcon("loader"),
    Shield: createIcon("shield"),
    ClipboardList: createIcon("clipboard-list"),
    Eye: createIcon("eye"),
    Plane: createIcon("plane"),
    Mountain: createIcon("mountain"),
    Radio: createIcon("radio"),
    Bot: createIcon("bot"),
    CalendarDays: createIcon("calendar-days"),
    CloudSun: createIcon("cloud-sun"),
    FileBarChart: createIcon("file-bar-chart"),
    BarChart3: createIcon("bar-chart-3"),
    ScanLine: createIcon("scan-line"),
    TestTubes: createIcon("test-tubes"),
    ArrowLeftRight: createIcon("arrow-left-right"),
    Target: createIcon("target"),
    Truck: createIcon("truck"),
    Handshake: createIcon("handshake"),
    Coins: createIcon("coins"),
    ShieldCheck: createIcon("shield-check"),
    Layers: createIcon("layers"),
    Wheat: createIcon("wheat"),
  };
});

// Mock @/lib/utils
vi.mock("@/lib/utils", () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(" "),
}));

import Sidebar from "../Sidebar";

describe("Sidebar", () => {
  it("renders logo and platform name", () => {
    render(<Sidebar />);
    expect(screen.getByText("سهول")).toBeInTheDocument();
    // "لوحة التحكم" appears in both logo subtitle and nav link
    expect(screen.getAllByText("لوحة التحكم").length).toBeGreaterThanOrEqual(1);
  });

  it("renders all main navigation sections", () => {
    render(<Sidebar />);

    // Section headers
    expect(screen.getByText("العمليات")).toBeInTheDocument();
    expect(screen.getByText("المراقبة")).toBeInTheDocument();
    expect(screen.getByText("الإدارة")).toBeInTheDocument();
    expect(screen.getByText("النظام")).toBeInTheDocument();
  });

  it("renders all navigation items", () => {
    render(<Sidebar />);

    // Main - appears in logo and nav
    expect(screen.getAllByText("لوحة التحكم").length).toBeGreaterThanOrEqual(1);

    // Operations
    expect(screen.getByText("المزارع")).toBeInTheDocument();
    expect(screen.getByText("إدارة الأمراض")).toBeInTheDocument();
    expect(screen.getByText("الري الذكي")).toBeInTheDocument();
    expect(screen.getByText("المهام")).toBeInTheDocument();

    // Monitoring
    expect(screen.getByText("المستشعرات")).toBeInTheDocument();
    expect(screen.getByText("التنبيهات")).toBeInTheDocument();
    expect(screen.getByText("مركز رصد الأوبئة")).toBeInTheDocument();
    expect(screen.getByText("حاسبة الإنتاجية")).toBeInTheDocument();

    // Management
    expect(screen.getByText("المستخدمون")).toBeInTheDocument();
    expect(screen.getByText("المعدات")).toBeInTheDocument();
    expect(screen.getByText("تتبع الأسطول")).toBeInTheDocument();
    expect(screen.getByText("التعاونيات")).toBeInTheDocument();
    expect(screen.getByText("المخزون")).toBeInTheDocument();
    expect(screen.getByText("السوق")).toBeInTheDocument();
    expect(screen.getByText("أسعار السوق")).toBeInTheDocument();
    expect(screen.getByText("التأمين الزراعي")).toBeInTheDocument();
    expect(screen.getByText("البذور والأصناف")).toBeInTheDocument();
    expect(screen.getByText("خريطة التربة")).toBeInTheDocument();
    expect(screen.getByText("البحوث")).toBeInTheDocument();

    // System
    expect(screen.getByText("الدعم الفني")).toBeInTheDocument();
    expect(screen.getByText("الإعدادات")).toBeInTheDocument();
  });

  it("renders expandable sections", () => {
    render(<Sidebar />);

    // Precision Agriculture section
    expect(screen.getByText("الزراعة الدقيقة")).toBeInTheDocument();

    // Analytics section
    expect(screen.getByText("التحليلات")).toBeInTheDocument();
  });

  it("expands precision agriculture submenu on click", () => {
    render(<Sidebar />);

    const precisionBtn = screen.getByText("الزراعة الدقيقة");
    fireEvent.click(precisionBtn);

    expect(screen.getByText("التطبيق المتغير (VRA)")).toBeInTheDocument();
    expect(screen.getByText("درجات النمو (GDD)")).toBeInTheDocument();
    expect(screen.getByText("إدارة الرش")).toBeInTheDocument();
    expect(screen.getByText("الري المحوري")).toBeInTheDocument();
  });

  it("expands analytics submenu on click", () => {
    render(<Sidebar />);

    const analyticsBtn = screen.getByText("التحليلات");
    fireEvent.click(analyticsBtn);

    expect(screen.getByText("تحليل الربحية")).toBeInTheDocument();
    expect(screen.getByText("تنبؤ الإنتاجية")).toBeInTheDocument();
    expect(screen.getByText("تحليلات الأقمار")).toBeInTheDocument();
  });

  it("renders user info section", () => {
    render(<Sidebar />);

    expect(screen.getByText("مدير النظام")).toBeInTheDocument();
    expect(screen.getByText("admin@sahool.io")).toBeInTheDocument();
  });

  it("renders logout button", () => {
    render(<Sidebar />);
    expect(screen.getByText("تسجيل الخروج")).toBeInTheDocument();
  });

  it("renders mobile menu button", () => {
    render(<Sidebar />);
    const menuButton = screen.getByLabelText("فتح القائمة");
    expect(menuButton).toBeInTheDocument();
  });

  it("has correct navigation links", () => {
    render(<Sidebar />);

    const dashboardLink = screen.getAllByRole("link").find(
      (link) => link.getAttribute("href") === "/dashboard",
    );
    expect(dashboardLink).toBeDefined();

    const farmsLink = screen.getAllByRole("link").find(
      (link) => link.getAttribute("href") === "/farms",
    );
    expect(farmsLink).toBeDefined();
  });

  it("shows support badge with count", () => {
    render(<Sidebar />);
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("renders navigation landmark", () => {
    render(<Sidebar />);
    expect(screen.getByLabelText("التنقل الرئيسي")).toBeInTheDocument();
  });

  it("highlights active route", () => {
    render(<Sidebar />);

    // /dashboard is the active route per mock
    const dashboardLinks = screen.getAllByRole("link").filter(
      (link) => link.getAttribute("href") === "/dashboard",
    );
    // The first dashboard link in main nav should have aria-current
    const mainDashLink = dashboardLinks.find((link) =>
      link.getAttribute("aria-current"),
    );
    expect(mainDashLink?.getAttribute("aria-current")).toBe("page");
  });
});
