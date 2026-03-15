/**
 * Sidebar Navigation Tests
 * اختبارات شريط التنقل الجانبي
 *
 * Verifies navigation links use correct routes (no /dashboard/ prefix),
 * version display, and accessibility attributes.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";

// Mock next/link
vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
    "aria-current"?: string;
    "aria-label"?: string;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

// Mock next/navigation
vi.mock("next/navigation", () => ({
  usePathname: vi.fn(() => "/dashboard"),
}));

// Mock next-intl
vi.mock("next-intl", () => ({
  useTranslations: vi.fn((namespace: string) => {
    const translations: Record<string, Record<string, string>> = {
      nav: {
        dashboard: "Dashboard",
        users: "Users",
        farms: "Farms",
        crops: "Crops",
        inventory: "Inventory",
        seasons: "Seasons",
        pivotIrrigation: "Pivot Irrigation",
        reports: "Reports",
        documents: "Documents",
        analytics: "Analytics",
        satellite: "Satellite",
        research: "Research",
        logistics: "Logistics",
        compliance: "Compliance",
        disasterAssessment: "Disaster Assessment",
        alerts: "Alerts",
        notifications: "Notifications",
        settings: "Settings",
        mainNav: "Main Navigation",
        version: "Version",
      },
      common: {
        appName: "SAHOOL",
        tagline: "Agricultural Intelligence",
      },
    };
    return (key: string) => translations[namespace]?.[key] || key;
  }),
}));

// Mock lucide-react icons
vi.mock("lucide-react", () => {
  const IconMock = ({ className, ...props }: { className?: string }) => (
    <svg className={className} {...props} data-testid="icon" />
  );
  return {
    LayoutDashboard: IconMock,
    Users: IconMock,
    Sprout: IconMock,
    FileText: IconMock,
    TrendingUp: IconMock,
    Settings: IconMock,
    Building2: IconMock,
    Package: IconMock,
    Calendar: IconMock,
    FileBarChart: IconMock,
    Droplets: IconMock,
    Satellite: IconMock,
    FlaskConical: IconMock,
    Truck: IconMock,
    Shield: IconMock,
    AlertTriangle: IconMock,
    Bell: IconMock,
  };
});

import { Sidebar } from "../sidebar";

describe("Sidebar Navigation", () => {
  describe("Route Correctness", () => {
    it("should render all navigation items", () => {
      render(<Sidebar />);

      // Check key navigation items are present
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
      expect(screen.getByText("Users")).toBeInTheDocument();
      expect(screen.getByText("Farms")).toBeInTheDocument();
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });

    it("should NOT use /dashboard/ prefix for routes", () => {
      render(<Sidebar />);

      const links = screen.getAllByRole("link");

      // Check that no links use /dashboard/ prefix (except /dashboard itself)
      const brokenLinks = links.filter((link) => {
        const href = link.getAttribute("href");
        return href && href.startsWith("/dashboard/");
      });

      expect(brokenLinks).toHaveLength(0);
    });

    it("should use correct href for Users (/users not /dashboard/users)", () => {
      render(<Sidebar />);

      const usersLink = screen.getByText("Users").closest("a");
      expect(usersLink).toHaveAttribute("href", "/users");
    });

    it("should use correct href for Farms (/farms not /dashboard/farms)", () => {
      render(<Sidebar />);

      const farmsLink = screen.getByText("Farms").closest("a");
      expect(farmsLink).toHaveAttribute("href", "/farms");
    });

    it("should use correct href for Crops (/crops)", () => {
      render(<Sidebar />);

      const link = screen.getByText("Crops").closest("a");
      expect(link).toHaveAttribute("href", "/crops");
    });

    it("should use correct href for Analytics (/analytics)", () => {
      render(<Sidebar />);

      const link = screen.getByText("Analytics").closest("a");
      expect(link).toHaveAttribute("href", "/analytics");
    });

    it("should use correct href for Satellite (/satellite)", () => {
      render(<Sidebar />);

      const link = screen.getByText("Satellite").closest("a");
      expect(link).toHaveAttribute("href", "/satellite");
    });

    it("should use correct href for Dashboard (/dashboard)", () => {
      render(<Sidebar />);

      // Dashboard link in nav items
      const navLinks = screen.getAllByText("Dashboard");
      const dashboardLink = navLinks[0]?.closest("a");
      expect(dashboardLink).toHaveAttribute("href", "/dashboard");
    });

    it("should use correct href for Settings (/settings)", () => {
      render(<Sidebar />);

      const link = screen.getByText("Settings").closest("a");
      expect(link).toHaveAttribute("href", "/settings");
    });

    it("should use correct href for Pivot Irrigation (/pivot-irrigation)", () => {
      render(<Sidebar />);

      const link = screen.getByText("Pivot Irrigation").closest("a");
      expect(link).toHaveAttribute("href", "/pivot-irrigation");
    });

    it("should use correct href for Disaster Assessment (/disaster-assessment)", () => {
      render(<Sidebar />);

      const link = screen.getByText("Disaster Assessment").closest("a");
      expect(link).toHaveAttribute("href", "/disaster-assessment");
    });
  });

  describe("Version Display", () => {
    it("should display version 16.0.0", () => {
      render(<Sidebar />);

      expect(screen.getByText(/16\.0\.0/)).toBeInTheDocument();
    });

    it("should NOT display version 17.0.0", () => {
      render(<Sidebar />);

      expect(screen.queryByText(/17\.0\.0/)).not.toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("should have navigation landmark role", () => {
      render(<Sidebar />);

      const navs = screen.getAllByRole("navigation");
      expect(navs.length).toBeGreaterThanOrEqual(1);
    });

    it("should have aria-label on navigation", () => {
      render(<Sidebar />);

      const nav = screen.getByRole("navigation", { name: "Main Navigation" });
      expect(nav).toBeInTheDocument();
    });

    it("should mark active page with aria-current", () => {
      render(<Sidebar />);

      // Dashboard is active (pathname = "/dashboard")
      const dashboardLinks = screen.getAllByText("Dashboard");
      const navDashboard = dashboardLinks[0]?.closest("a");
      expect(navDashboard).toHaveAttribute("aria-current", "page");
    });

    it("should render the app name", () => {
      render(<Sidebar />);

      expect(screen.getByText("SAHOOL")).toBeInTheDocument();
    });
  });
});
