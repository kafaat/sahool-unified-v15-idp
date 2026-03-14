/**
 * Page Rendering Tests - Phase 2 Coverage
 * اختبارات عرض الصفحات - المرحلة الثانية
 *
 * Integration tests that render pages and verify key UI elements.
 * Covers dashboard, users, alerts, farms, and other core pages.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import React from "react";

// ═══════════════════════════════════════════════════════════════════════════
// Global Mocks
// ═══════════════════════════════════════════════════════════════════════════

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => "/dashboard",
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}));

// Mock next/dynamic to render the component inline (skip SSR checks)
vi.mock("next/dynamic", () => ({
  default: (_loader: () => Promise<{ default: React.ComponentType }>, _opts?: unknown) => {
    // Return a simple placeholder since dynamic imports are complex in test
    const DynamicComponent = (props: Record<string, unknown>) => {
      return React.createElement("div", { "data-testid": "dynamic-component", ...props });
    };
    DynamicComponent.displayName = "DynamicComponent";
    return DynamicComponent;
  },
}));

// Mock next/link
vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) =>
    React.createElement("a", { href, ...props }, children),
}));

// Mock all API functions from lib/api
vi.mock("@/lib/api", () => ({
  fetchDashboardStats: vi.fn().mockResolvedValue({
    totalFarms: 150,
    activeFarms: 120,
    totalArea: 5000,
    totalCrops: 25,
    pendingAlerts: 8,
    avgNdvi: 0.65,
    waterUsage: 2500,
  }),
  fetchFarms: vi.fn().mockResolvedValue([
    { id: "1", name: "مزرعة الرشيد", area: 50, status: "active", location: { lat: 24.7, lng: 46.7 } },
    { id: "2", name: "مزرعة النخيل", area: 30, status: "active", location: { lat: 24.8, lng: 46.8 } },
  ]),
  fetchDiagnoses: vi.fn().mockResolvedValue([]),
  fetchYieldTrends: vi.fn().mockResolvedValue([]),
  fetchCropDistribution: vi.fn().mockResolvedValue([]),
  fetchWeeklyActivity: vi.fn().mockResolvedValue([]),
  fetchPlatformMetrics: vi.fn().mockResolvedValue({}),
  apiClient: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
  userService: {
    getAll: vi.fn().mockResolvedValue({ data: [], total: 0, page: 1, totalPages: 1 }),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  alertService: {
    getAll: vi.fn().mockResolvedValue({ data: [], total: 0, page: 1, totalPages: 1 }),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    acknowledge: vi.fn(),
    resolve: vi.fn(),
  },
  farmService: {
    getAll: vi.fn().mockResolvedValue({ data: [], total: 0, page: 1, totalPages: 1 }),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  API_URLS: {},
}));

// Mock lib/api-client
vi.mock("@/lib/api-client", () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
}));

// Mock lib/logger
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

// Mock WebSocket hooks
vi.mock("@/hooks/useWebSocket", () => ({
  useWebSocket: () => ({ isConnected: false, messages: [] }),
  useWebSocketEvent: () => null,
}));

vi.mock("@/hooks/useRealTimeAlerts", () => ({
  useRealTimeAlerts: () => ({ alerts: [], isConnected: false, unreadCount: 0, criticalAlerts: [] }),
}));

// Mock layout components
vi.mock("@/components/layout/Header", () => ({
  default: ({ title }: { title?: string }) =>
    React.createElement("header", { "data-testid": "header" }, title || "Header"),
}));

// Mock chart components
vi.mock("../../dashboard/DashboardCharts.dynamic", () => ({
  YieldTrendChart: () => React.createElement("div", { "data-testid": "yield-chart" }),
  WeeklyActivityChart: () => React.createElement("div", { "data-testid": "activity-chart" }),
  CropDistributionChart: () => React.createElement("div", { "data-testid": "crop-chart" }),
}));

// Mock UI components that are tested separately
vi.mock("@/components/ui/StatCard", () => ({
  default: ({ title, value }: { title: string; value: string | number }) =>
    React.createElement("div", { "data-testid": `stat-${title}` }, `${title}: ${value}`),
}));

vi.mock("@/components/ui/AlertBadge", () => ({
  default: ({ count }: { count?: number }) =>
    React.createElement("span", { "data-testid": "alert-badge" }, count),
}));

vi.mock("@/components/ui/DataTable", () => ({
  default: ({ data, columns }: { data: unknown[]; columns: unknown[] }) =>
    React.createElement("table", { "data-testid": "data-table" },
      React.createElement("tbody", null,
        React.createElement("tr", null,
          React.createElement("td", null, `${data?.length || 0} rows`),
        ),
      ),
    ),
}));

vi.mock("@/components/ui/StatusBadge", () => ({
  default: ({ status }: { status: string }) =>
    React.createElement("span", { "data-testid": "status-badge" }, status),
}));

// Mock config/api
vi.mock("@/config/api", () => ({
  API_URL: "http://localhost:8000",
  API_BASE_URL: "http://localhost:8000",
  API_URLS: {},
  API_CONFIG: { timeout: 30000 },
  TIMEOUT_TIERS: { default: 30000 },
  SERVICE_URLS: {},
}));

// Mock auth store so auth pages don't need a real AuthProvider
vi.mock("@/stores/auth.store", () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) =>
    React.createElement("div", { "data-testid": "auth-provider" }, children),
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: vi.fn().mockResolvedValue({}),
    logout: vi.fn(),
    checkAuth: vi.fn().mockResolvedValue(undefined),
  }),
}));

// ═══════════════════════════════════════════════════════════════════════════
// Dashboard Page Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Dashboard Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders without crashing", async () => {
    const DashboardPage = (await import("@/app/dashboard/page")).default;
    const { container } = render(React.createElement(DashboardPage));
    expect(container).toBeTruthy();
  });

  it("calls fetchDashboardStats on mount", async () => {
    const { fetchDashboardStats } = await import("@/lib/api");
    const DashboardPage = (await import("@/app/dashboard/page")).default;

    render(React.createElement(DashboardPage));

    await waitFor(() => {
      expect(fetchDashboardStats).toHaveBeenCalled();
    });
  });

  it("calls fetchFarms on mount", async () => {
    const { fetchFarms } = await import("@/lib/api");
    const DashboardPage = (await import("@/app/dashboard/page")).default;

    render(React.createElement(DashboardPage));

    await waitFor(() => {
      expect(fetchFarms).toHaveBeenCalled();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Users Page Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Users Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders without crashing", async () => {
    const UsersPage = (await import("@/app/users/page")).default;
    const { container } = render(React.createElement(UsersPage));
    expect(container).toBeTruthy();
  });

  it("renders header with users icon context", async () => {
    const UsersPage = (await import("@/app/users/page")).default;
    render(React.createElement(UsersPage));

    expect(screen.getByTestId("header")).toBeInTheDocument();
  });

  it("calls userService.getAll on mount", async () => {
    const { userService } = await import("@/lib/api");
    const UsersPage = (await import("@/app/users/page")).default;

    render(React.createElement(UsersPage));

    await waitFor(() => {
      expect(userService.getAll).toHaveBeenCalled();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Alerts Page Tests
// ═══════════════════════════════════════════════════════════════════════════

describe("Alerts Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders without crashing", async () => {
    const AlertsPage = (await import("@/app/alerts/page")).default;
    const { container } = render(React.createElement(AlertsPage));
    expect(container).toBeTruthy();
  });

  it("calls alertService.getAll on mount", async () => {
    const { alertService } = await import("@/lib/api");
    const AlertsPage = (await import("@/app/alerts/page")).default;

    render(React.createElement(AlertsPage));

    await waitFor(() => {
      expect(alertService.getAll).toHaveBeenCalled();
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Auth Pages Tests (login, register, forgot-password)
// ═══════════════════════════════════════════════════════════════════════════

describe("Login Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders without crashing", async () => {
    const LoginPage = (await import("@/app/(auth)/login/page")).default;
    const { container } = render(React.createElement(LoginPage));
    expect(container).toBeTruthy();
  });
});

describe("Register Page", () => {
  it("renders without crashing", async () => {
    const RegisterPage = (await import("@/app/(auth)/register/page")).default;
    const { container } = render(React.createElement(RegisterPage));
    expect(container).toBeTruthy();
  });
});

describe("Forgot Password Page", () => {
  it("renders without crashing", async () => {
    const ForgotPasswordPage = (
      await import("@/app/(auth)/forgot-password/page")
    ).default;
    const { container } = render(React.createElement(ForgotPasswordPage));
    expect(container).toBeTruthy();
  });
});
