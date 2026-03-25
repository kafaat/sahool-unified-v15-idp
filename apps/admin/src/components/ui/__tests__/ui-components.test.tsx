/**
 * UI Component Tests
 * اختبارات مكونات واجهة المستخدم
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: () => '/dashboard',
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
  }),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
  } & Record<string, unknown>) => React.createElement('a', { href, ...props }, children),
}));

// Mock lucide-react icons with explicit named exports
vi.mock('lucide-react', () => {
  const _React = require('react');
  const _createIcon = (name: string) => {
    const Icon = (props: Record<string, unknown>) =>
      _React.createElement('svg', { 'data-testid': `icon-${name}`, ...props });
    Icon.displayName = name;
    return Icon;
  };
  return {
    __esModule: true,
    TrendingUp: _createIcon('TrendingUp'),
    TrendingDown: _createIcon('TrendingDown'),
    ArrowUp: _createIcon('ArrowUp'),
    ArrowDown: _createIcon('ArrowDown'),
    Activity: _createIcon('Activity'),
    ChevronRight: _createIcon('ChevronRight'),
    ChevronLeft: _createIcon('ChevronLeft'),
    Home: _createIcon('Home'),
    AlertTriangle: _createIcon('AlertTriangle'),
    CheckCircle: _createIcon('CheckCircle'),
    XCircle: _createIcon('XCircle'),
    Info: _createIcon('Info'),
    AlertCircle: _createIcon('AlertCircle'),
  };
});

// Mock @/lib/utils with all needed exports
vi.mock('@/lib/utils', () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(' '),
  getStatusColor: (status: string) => {
    const colors: Record<string, string> = {
      active: 'text-green-600 bg-green-100',
      inactive: 'text-red-600 bg-red-100',
      pending: 'text-yellow-600 bg-yellow-100',
      confirmed: 'text-blue-600 bg-blue-100',
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  },
  getSeverityColor: (severity: string) => {
    const colors: Record<string, string> = {
      low: 'text-green-600 bg-green-100',
      medium: 'text-yellow-600 bg-yellow-100',
      high: 'text-orange-600 bg-orange-100',
      critical: 'text-red-600 bg-red-100',
    };
    return colors[severity] || 'text-gray-600 bg-gray-100';
  },
  getStatusLabel: (status: string) => {
    const labels: Record<string, string> = {
      active: 'نشط',
      inactive: 'غير نشط',
      pending: 'قيد المراجعة',
      confirmed: 'مؤكد',
    };
    return labels[status] || status;
  },
  getSeverityLabel: (severity: string) => {
    const labels: Record<string, string> = {
      low: 'منخفض',
      medium: 'متوسط',
      high: 'مرتفع',
      critical: 'حرج',
    };
    return labels[severity] || severity;
  },
  formatDate: (date: string) => date,
  formatNumber: (num: number) => String(num),
  formatArea: (hectares: number) => `${hectares} هكتار`,
}));

// Import components after mocks - these are default exports
import StatCard from '../StatCard';
import StatusBadge from '../StatusBadge';
import AlertBadge from '../AlertBadge';
import Breadcrumbs from '../Breadcrumbs';

// Helper: create a mock icon component
const MockIcon = (props: Record<string, unknown>) =>
  React.createElement('svg', { 'data-testid': 'mock-icon', ...props });

describe('StatCard', () => {
  it('renders title and value', () => {
    render(<StatCard title="المزارع النشطة" value="125" icon={MockIcon} />);
    expect(screen.getByText('المزارع النشطة')).toBeInTheDocument();
    expect(screen.getByText('125')).toBeInTheDocument();
  });

  it('renders numeric value formatted', () => {
    render(<StatCard title="المحاصيل" value={1250} icon={MockIcon} />);
    expect(screen.getByText('1250')).toBeInTheDocument();
  });

  it('renders trend information', () => {
    render(
      <StatCard
        title="الإنتاج"
        value="1000"
        icon={MockIcon}
        trend={{ value: 12.5, isPositive: true }}
      />
    );
    expect(screen.getByText(/12.5/)).toBeInTheDocument();
  });

  it('renders with icon', () => {
    render(<StatCard title="Test" value="100" icon={MockIcon} />);
    expect(screen.getByTestId('mock-icon')).toBeInTheDocument();
  });

  it('renders suffix when provided', () => {
    render(<StatCard title="المساحة" value={10} icon={MockIcon} suffix="هكتار" />);
    expect(screen.getByText('هكتار')).toBeInTheDocument();
  });
});

describe('StatusBadge', () => {
  it('renders status text', () => {
    render(<StatusBadge status="active" />);
    expect(screen.getByText('نشط')).toBeInTheDocument();
  });

  it('renders different statuses', () => {
    const { rerender } = render(<StatusBadge status="pending" />);
    expect(screen.getByText('قيد المراجعة')).toBeInTheDocument();

    rerender(<StatusBadge status="confirmed" />);
    expect(screen.getByText('مؤكد')).toBeInTheDocument();
  });

  it('applies correct color classes for active status', () => {
    const { container } = render(<StatusBadge status="active" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('green');
  });
});

describe('AlertBadge', () => {
  it('renders severity text', () => {
    render(<AlertBadge severity="critical" />);
    expect(screen.getByText('حرج')).toBeInTheDocument();
  });

  it('renders different severities', () => {
    const { rerender } = render(<AlertBadge severity="low" />);
    expect(screen.getByText('منخفض')).toBeInTheDocument();

    rerender(<AlertBadge severity="medium" />);
    expect(screen.getByText('متوسط')).toBeInTheDocument();

    rerender(<AlertBadge severity="high" />);
    expect(screen.getByText('مرتفع')).toBeInTheDocument();
  });

  it('applies correct color for critical severity', () => {
    const { container } = render(<AlertBadge severity="critical" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('red');
  });
});

describe('Breadcrumbs', () => {
  it('renders breadcrumb items', () => {
    render(
      <Breadcrumbs
        showHome={false}
        items={[
          { label: 'الرئيسية', href: '/' },
          { label: 'المزارع', href: '/farms' },
          { label: 'حقل 1' },
        ]}
      />
    );

    expect(screen.getByText('الرئيسية')).toBeInTheDocument();
    expect(screen.getByText('المزارع')).toBeInTheDocument();
    expect(screen.getByText('حقل 1')).toBeInTheDocument();
  });

  it('makes last item non-clickable', () => {
    render(
      <Breadcrumbs
        showHome={false}
        items={[{ label: 'الرئيسية', href: '/' }, { label: 'الحالي' }]}
      />
    );

    // Last item should be a span, not a link
    const lastItem = screen.getByText('الحالي');
    expect(lastItem.tagName).not.toBe('A');
  });
});
