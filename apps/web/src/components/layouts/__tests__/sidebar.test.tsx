/**
 * Sidebar Navigation Tests (Client/Farmer App)
 * اختبارات شريط التنقل الجانبي (تطبيق المزارع)
 *
 * Verifies navigation links use correct routes (no /dashboard/ prefix),
 * version display, accessibility attributes, and that admin-only
 * features are NOT present in the client sidebar.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Mock next/link
vi.mock('next/link', () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
    'aria-current'?: string;
    'aria-label'?: string;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: vi.fn(() => '/dashboard'),
}));

// Mock next-intl
vi.mock('next-intl', () => ({
  useTranslations: vi.fn((namespace: string) => {
    const translations: Record<string, Record<string, string>> = {
      nav: {
        dashboard: 'Dashboard',
        farms: 'Farms',
        fields: 'Fields',
        crops: 'Crops',
        inventory: 'Inventory',
        seasons: 'Seasons',
        tasks: 'Tasks',
        pivotIrrigation: 'Pivot Irrigation',
        irrigation: 'Irrigation',
        cropHealth: 'Crop Health',
        diseases: 'Diseases',
        weather: 'Weather',
        satellite: 'Satellite',
        yield: 'Yield',
        precisionAgriculture: 'Precision Agriculture',
        iot: 'IoT',
        sensors: 'Sensors',
        equipment: 'Equipment',
        marketplace: 'Marketplace',
        wallet: 'Wallet',
        community: 'Community',
        logistics: 'Logistics',
        reports: 'Reports',
        documents: 'Documents',
        analytics: 'Analytics',
        disasterAssessment: 'Disaster Assessment',
        alerts: 'Alerts',
        notifications: 'Notifications',
        copilot: 'Copilot',
        support: 'Support',
        settings: 'Settings',
        mainNav: 'Main Navigation',
        version: 'Version',
        overview: 'Overview',
        farmManagement: 'Farm Management',
        waterAndIrrigation: 'Water & Irrigation',
        cropIntelligence: 'Crop Intelligence',
        iotAndEquipment: 'IoT & Equipment',
        businessAndCommunity: 'Business & Community',
        reportsAndDocs: 'Reports & Docs',
        alertsAndNotifications: 'Alerts & Notifications',
        tools: 'Tools',
        closeMenu: 'Close Menu',
      },
      common: {
        appName: 'SAHOOL',
        tagline: 'Agricultural Intelligence',
      },
    };
    return (key: string) => translations[namespace]?.[key] || key;
  }),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => {
  const IconMock = ({ className, ...props }: { className?: string }) => (
    <svg className={className} {...props} data-testid="icon" />
  );
  return {
    LayoutDashboard: IconMock,
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
    Truck: IconMock,
    AlertTriangle: IconMock,
    Bell: IconMock,
    X: IconMock,
    MapPin: IconMock,
    CloudSun: IconMock,
    ListChecks: IconMock,
    Wrench: IconMock,
    Cpu: IconMock,
    Activity: IconMock,
    ShoppingCart: IconMock,
    Users: IconMock,
    HeartPulse: IconMock,
    Wallet: IconMock,
    BarChart3: IconMock,
    Crosshair: IconMock,
    Bot: IconMock,
    HelpCircle: IconMock,
    Bug: IconMock,
    Radar: IconMock,
  };
});

import { Sidebar } from '../sidebar';

describe('Sidebar Navigation (Client/Farmer)', () => {
  describe('Route Correctness', () => {
    it('should render all farmer navigation items', () => {
      render(<Sidebar />);

      // Check key farmer navigation items are present
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Farms')).toBeInTheDocument();
      expect(screen.getByText('Crops')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('should NOT use /dashboard/ prefix for routes', () => {
      render(<Sidebar />);

      const links = screen.getAllByRole('link');

      // Check that no links use /dashboard/ prefix (except /dashboard itself)
      const brokenLinks = links.filter((link) => {
        const href = link.getAttribute('href');
        return href && href.startsWith('/dashboard/');
      });

      expect(brokenLinks).toHaveLength(0);
    });

    it('should use correct href for Farms (/farms not /dashboard/farms)', () => {
      render(<Sidebar />);

      const farmsLink = screen.getByText('Farms').closest('a');
      expect(farmsLink).toHaveAttribute('href', '/farms');
    });

    it('should use correct href for Crops (/crops)', () => {
      render(<Sidebar />);

      const link = screen.getByText('Crops').closest('a');
      expect(link).toHaveAttribute('href', '/crops');
    });

    it('should use correct href for Analytics (/analytics)', () => {
      render(<Sidebar />);

      const link = screen.getByText('Analytics').closest('a');
      expect(link).toHaveAttribute('href', '/analytics');
    });

    it('should use correct href for Satellite (/satellite)', () => {
      render(<Sidebar />);

      const link = screen.getByText('Satellite').closest('a');
      expect(link).toHaveAttribute('href', '/satellite');
    });

    it('should use correct href for Dashboard (/dashboard)', () => {
      render(<Sidebar />);

      const navLinks = screen.getAllByText('Dashboard');
      const dashboardLink = navLinks[0]?.closest('a');
      expect(dashboardLink).toHaveAttribute('href', '/dashboard');
    });

    it('should use correct href for Settings (/settings)', () => {
      render(<Sidebar />);

      const link = screen.getByText('Settings').closest('a');
      expect(link).toHaveAttribute('href', '/settings');
    });

    it('should use correct href for Pivot Irrigation (/pivot-irrigation)', () => {
      render(<Sidebar />);

      const link = screen.getByText('Pivot Irrigation').closest('a');
      expect(link).toHaveAttribute('href', '/pivot-irrigation');
    });

    it('should use correct href for Disaster Assessment (/disaster-assessment)', () => {
      render(<Sidebar />);

      const link = screen.getByText('Disaster Assessment').closest('a');
      expect(link).toHaveAttribute('href', '/disaster-assessment');
    });
  });

  describe('Admin-Only Features NOT Present', () => {
    it('should NOT show Users link (admin-only)', () => {
      render(<Sidebar />);
      expect(screen.queryByText('Users')).not.toBeInTheDocument();
    });

    it('should NOT show Research link (admin-only)', () => {
      render(<Sidebar />);
      expect(screen.queryByText('Research')).not.toBeInTheDocument();
    });

    it('should NOT show Compliance link (admin-only)', () => {
      render(<Sidebar />);
      expect(screen.queryByText('Compliance')).not.toBeInTheDocument();
    });
  });

  describe('Version Display', () => {
    it('should display version 16.0.0', () => {
      render(<Sidebar />);

      expect(screen.getByText(/16\.0\.0/)).toBeInTheDocument();
    });

    it('should NOT display version 17.0.0', () => {
      render(<Sidebar />);

      expect(screen.queryByText(/17\.0\.0/)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have navigation landmark role', () => {
      render(<Sidebar />);

      const navs = screen.getAllByRole('navigation');
      expect(navs.length).toBeGreaterThanOrEqual(1);
    });

    it('should have aria-label on navigation', () => {
      render(<Sidebar />);

      const nav = screen.getByRole('navigation', { name: 'Main Navigation' });
      expect(nav).toBeInTheDocument();
    });

    it('should mark active page with aria-current', () => {
      render(<Sidebar />);

      // Dashboard is active (pathname = "/dashboard")
      const dashboardLinks = screen.getAllByText('Dashboard');
      const navDashboard = dashboardLinks[0]?.closest('a');
      expect(navDashboard).toHaveAttribute('aria-current', 'page');
    });

    it('should render the app name', () => {
      render(<Sidebar />);

      expect(screen.getByText('SAHOOL')).toBeInTheDocument();
    });
  });

  describe('Mobile Drawer', () => {
    it('should render mobile drawer when isOpen is true', () => {
      const onClose = vi.fn();
      render(<Sidebar isOpen={true} onClose={onClose} />);

      const drawer = screen.getByTestId('mobile-drawer');
      expect(drawer).toBeInTheDocument();
    });

    it('should NOT render mobile drawer when isOpen is false', () => {
      const onClose = vi.fn();
      render(<Sidebar isOpen={false} onClose={onClose} />);

      expect(screen.queryByTestId('mobile-drawer')).not.toBeInTheDocument();
    });

    it('should call onClose when backdrop is clicked', () => {
      const onClose = vi.fn();
      render(<Sidebar isOpen={true} onClose={onClose} />);

      const initialCalls = onClose.mock.calls.length;
      const backdrop = screen.getByTestId('mobile-drawer-backdrop');
      fireEvent.click(backdrop);
      expect(onClose).toHaveBeenCalledTimes(initialCalls + 1);
    });

    it('should render without drawer props (backward compatible)', () => {
      render(<Sidebar />);

      // Desktop sidebar should still render
      const sidebar = screen.getByTestId('desktop-sidebar');
      expect(sidebar).toBeInTheDocument();

      // No drawer should be present
      expect(screen.queryByTestId('mobile-drawer')).not.toBeInTheDocument();
    });
  });
});
