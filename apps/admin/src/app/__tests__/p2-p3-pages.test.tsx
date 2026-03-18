/**
 * P2/P3 Feature Pages Tests
 * اختبارات صفحات ميزات P2/P3
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// ═══════════════════════════════════════════════════════════════════════════
// Global Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock("next/navigation", () => ({
  usePathname: () => "/analytics/yield-forecasting",
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
    refresh: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

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

vi.mock("next/dynamic", () => ({
  default: (_loader: () => Promise<{ default: React.ComponentType }>, _opts?: unknown) => {
    const DynamicComponent = (props: Record<string, unknown>) =>
      React.createElement("div", { "data-testid": "dynamic-component", ...props });
    DynamicComponent.displayName = "DynamicComponent";
    return DynamicComponent;
  },
}));

vi.mock("@/lib/logger", () => ({
  logger: {
    log: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
    production: vi.fn(),
    critical: vi.fn(),
  },
}));

vi.mock("@/stores/auth.store", () => ({
  useAuth: () => ({
    user: { id: "1", email: "admin@sahool.io", name: "Admin", name_ar: "مدير", role: "admin" },
    isAuthenticated: true,
    isLoading: false,
    logout: vi.fn(),
    login: vi.fn(),
    checkAuth: vi.fn(),
  }),
}));

vi.mock("@/stores/theme.store", () => ({
  useTheme: () => ({
    theme: "light",
    resolvedTheme: "light",
    setTheme: vi.fn(),
    toggleTheme: vi.fn(),
  }),
}));

vi.mock("@/lib/utils", () => ({
  cn: (...inputs: (string | undefined | null | false)[]) =>
    inputs.filter(Boolean).join(" "),
}));

vi.mock("@/components/layout/Header", () => ({
  default: ({ title, subtitle }: { title: string; subtitle?: string }) =>
    React.createElement(
      "header",
      { "data-testid": "header" },
      React.createElement("h1", { "data-testid": "header-title" }, title),
      subtitle && React.createElement("p", { "data-testid": "header-subtitle" }, subtitle),
    ),
}));

vi.mock("@/components/ui/StatCard", () => ({
  default: ({ title, value }: { title: string; value: string | number; [key: string]: unknown }) =>
    React.createElement(
      "div",
      { "data-testid": "stat-card" },
      React.createElement("span", { "data-testid": "stat-title" }, title),
      React.createElement("span", { "data-testid": "stat-value" }, String(value)),
    ),
}));

// Explicit lucide-react mock — Proxy-based mocks hang on dynamic import
vi.mock("lucide-react", () => {
  const createIcon = (name: string) => {
    const Icon = (props: Record<string, unknown>) =>
      React.createElement("svg", { "data-testid": `icon-${name}`, ...props });
    Icon.displayName = name;
    return Icon;
  };
  return {
    // Yield Forecasting
    TrendingUp: createIcon("TrendingUp"),
    BarChart3: createIcon("BarChart3"),
    Leaf: createIcon("Leaf"),
    Calendar: createIcon("Calendar"),
    CheckCircle2: createIcon("CheckCircle2"),
    ChevronDown: createIcon("ChevronDown"),
    Droplets: createIcon("Droplets"),
    Sun: createIcon("Sun"),
    FlaskConical: createIcon("FlaskConical"),
    AlertTriangle: createIcon("AlertTriangle"),
    Target: createIcon("Target"),
    Clock: createIcon("Clock"),
    MapPin: createIcon("MapPin"),
    Activity: createIcon("Activity"),
    // Fleet Tracking
    Tractor: createIcon("Tractor"),
    Plane: createIcon("Plane"),
    SprayCan: createIcon("SprayCan"),
    Truck: createIcon("Truck"),
    Wrench: createIcon("Wrench"),
    Gauge: createIcon("Gauge"),
    Fuel: createIcon("Fuel"),
    ChevronRight: createIcon("ChevronRight"),
    X: createIcon("X"),
    RefreshCw: createIcon("RefreshCw"),
    Filter: createIcon("Filter"),
    PauseCircle: createIcon("PauseCircle"),
    WifiOff: createIcon("WifiOff"),
    Navigation: createIcon("Navigation"),
    Thermometer: createIcon("Thermometer"),
    Battery: createIcon("Battery"),
    Shield: createIcon("Shield"),
    // Cooperatives
    Users: createIcon("Users"),
    Layers: createIcon("Layers"),
    Package: createIcon("Package"),
    DollarSign: createIcon("DollarSign"),
    XCircle: createIcon("XCircle"),
    Wheat: createIcon("Wheat"),
    ShoppingCart: createIcon("ShoppingCart"),
    Factory: createIcon("Factory"),
    User: createIcon("User"),
    BookOpen: createIcon("BookOpen"),
    Box: createIcon("Box"),
    // Market Prices
    TrendingDown: createIcon("TrendingDown"),
    Minus: createIcon("Minus"),
    BarChart2: createIcon("BarChart2"),
    Bell: createIcon("Bell"),
    ShoppingBasket: createIcon("ShoppingBasket"),
    Store: createIcon("Store"),
    Download: createIcon("Download"),
    Star: createIcon("Star"),
    ArrowUpRight: createIcon("ArrowUpRight"),
    ArrowDownRight: createIcon("ArrowDownRight"),
    Award: createIcon("Award"),
    // Insurance
    FileText: createIcon("FileText"),
    AlertCircle: createIcon("AlertCircle"),
    CloudRain: createIcon("CloudRain"),
    Bug: createIcon("Bug"),
    CloudSnow: createIcon("CloudSnow"),
    Waves: createIcon("Waves"),
    CheckCircle: createIcon("CheckCircle"),
    Info: createIcon("Info"),
    // Soil Map
    Map: createIcon("Map"),
    TreePine: createIcon("TreePine"),
    Mountain: createIcon("Mountain"),
    Wind: createIcon("Wind"),
    ChevronUp: createIcon("ChevronUp"),
    ArrowRight: createIcon("ArrowRight"),
    // Seeds
    Search: createIcon("Search"),
    Coffee: createIcon("Coffee"),
    Cherry: createIcon("Cherry"),
    Apple: createIcon("Apple"),
    ChevronLeft: createIcon("ChevronLeft"),
    Globe: createIcon("Globe"),
    Sprout: createIcon("Sprout"),
  };
});

// ═══════════════════════════════════════════════════════════════════════════
// 1. Yield Forecasting — تنبؤ الإنتاجية
// ═══════════════════════════════════════════════════════════════════════════

describe("Yield Forecasting Page", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders header with correct title", async () => {
    const Page = (await import("@/app/analytics/yield-forecasting/page")).default;
    render(React.createElement(Page));
    expect(screen.getByTestId("header-title")).toHaveTextContent("تنبؤ الإنتاجية");
  });

  it("renders 4 stat cards", async () => {
    const Page = (await import("@/app/analytics/yield-forecasting/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId("stat-card").length).toBe(4);
  });

  it("displays field prediction data", async () => {
    const Page = (await import("@/app/analytics/yield-forecasting/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/قمح/).length).toBeGreaterThan(0);
  });

  it("has filter tabs for crop types", async () => {
    const Page = (await import("@/app/analytics/yield-forecasting/page")).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 2. Fleet Tracking — تتبع الأسطول
// ═══════════════════════════════════════════════════════════════════════════

describe("Fleet Tracking Page", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders header with correct title", async () => {
    const Page = (await import("@/app/equipment/fleet-tracking/page")).default;
    render(React.createElement(Page));
    expect(screen.getByTestId("header-title")).toHaveTextContent("تتبع الأسطول");
  });

  it("renders stat cards", async () => {
    const Page = (await import("@/app/equipment/fleet-tracking/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId("stat-card").length).toBeGreaterThanOrEqual(1);
  });

  it("shows equipment mock data", async () => {
    const Page = (await import("@/app/equipment/fleet-tracking/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/جرار|طائرة|حصّادة|مرش|مضخة|شاحنة|رشاش/).length).toBeGreaterThan(0);
  });

  it("has filter controls", async () => {
    const Page = (await import("@/app/equipment/fleet-tracking/page")).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 3. Cooperatives — إدارة التعاونيات
// ═══════════════════════════════════════════════════════════════════════════

describe("Cooperatives Page", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders header with correct title", async () => {
    const Page = (await import("@/app/cooperatives/page")).default;
    render(React.createElement(Page));
    expect(screen.getByTestId("header-title")).toHaveTextContent("إدارة التعاونيات");
  });

  it("renders stat cards", async () => {
    const Page = (await import("@/app/cooperatives/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId("stat-card").length).toBeGreaterThanOrEqual(1);
  });

  it("shows cooperative data", async () => {
    const Page = (await import("@/app/cooperatives/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/تعاونية/).length).toBeGreaterThan(0);
  });

  it("has interactive elements", async () => {
    const Page = (await import("@/app/cooperatives/page")).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 4. Market Prices — أسعار السوق
// ═══════════════════════════════════════════════════════════════════════════

describe("Market Prices Page", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders header with correct title", async () => {
    const Page = (await import("@/app/market-prices/page")).default;
    render(React.createElement(Page));
    expect(screen.getByTestId("header-title")).toHaveTextContent("أسعار السوق");
  });

  it("renders stat cards", async () => {
    const Page = (await import("@/app/market-prices/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId("stat-card").length).toBeGreaterThanOrEqual(1);
  });

  it("shows crop price data", async () => {
    const Page = (await import("@/app/market-prices/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/قمح/).length).toBeGreaterThan(0);
  });

  it("has filter controls", async () => {
    const Page = (await import("@/app/market-prices/page")).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 5. Insurance — التأمين الزراعي
// ═══════════════════════════════════════════════════════════════════════════

describe("Insurance Page", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders header with correct title", async () => {
    const Page = (await import("@/app/insurance/page")).default;
    render(React.createElement(Page));
    expect(screen.getByTestId("header-title")).toHaveTextContent("التأمين الزراعي");
  });

  it("renders stat cards", async () => {
    const Page = (await import("@/app/insurance/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId("stat-card").length).toBeGreaterThanOrEqual(1);
  });

  it("shows policy data", async () => {
    const Page = (await import("@/app/insurance/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/POL-|أحمد|محمد|علي|خالد/).length).toBeGreaterThan(0);
  });

  it("has tab navigation", async () => {
    const Page = (await import("@/app/insurance/page")).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 6. Soil Map — خريطة التربة اليمنية
// ═══════════════════════════════════════════════════════════════════════════

describe("Soil Map Page", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders header with correct title", async () => {
    const Page = (await import("@/app/soil-map/page")).default;
    render(React.createElement(Page));
    expect(screen.getByTestId("header-title")).toHaveTextContent("خريطة التربة اليمنية");
  });

  it("renders stat cards", async () => {
    const Page = (await import("@/app/soil-map/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId("stat-card").length).toBeGreaterThanOrEqual(1);
  });

  it("shows agro-ecological zone data", async () => {
    const Page = (await import("@/app/soil-map/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText("تهامة").length).toBeGreaterThan(0);
  });

  it("shows highland zone", async () => {
    const Page = (await import("@/app/soil-map/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/المرتفعات/).length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 7. Seeds Catalog — كتالوج البذور والأصناف
// ═══════════════════════════════════════════════════════════════════════════

describe("Seeds Catalog Page", () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it("renders header with correct title", async () => {
    const Page = (await import("@/app/seeds/page")).default;
    render(React.createElement(Page));
    expect(screen.getByTestId("header-title")).toHaveTextContent("كتالوج البذور والأصناف");
  });

  it("renders stat cards", async () => {
    const Page = (await import("@/app/seeds/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId("stat-card").length).toBeGreaterThanOrEqual(1);
  });

  it("shows variety data", async () => {
    const Page = (await import("@/app/seeds/page")).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/قمح|بن|ذرة|نخيل|طماطم/).length).toBeGreaterThan(0);
  });

  it("has filter controls", async () => {
    const Page = (await import("@/app/seeds/page")).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThan(0);
  });
});
