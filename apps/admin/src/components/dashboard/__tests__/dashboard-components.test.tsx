/**
 * Dashboard Component Tests
 * اختبارات مكونات لوحة التحكم
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: () => '/dashboard',
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
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

// Mock next/dynamic
vi.mock('next/dynamic', () => ({
  default: () => {
    const DynamicComponent = () =>
      React.createElement('div', { 'data-testid': 'dynamic-map' }, 'Map');
    DynamicComponent.displayName = 'DynamicComponent';
    return DynamicComponent;
  },
}));

// Mock lucide-react icons
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
    Activity: _createIcon('Activity'),
    AlertTriangle: _createIcon('AlertTriangle'),
    Bell: _createIcon('Bell'),
    Bug: _createIcon('Bug'),
    Calendar: _createIcon('Calendar'),
    CheckCircle: _createIcon('CheckCircle'),
    Droplets: _createIcon('Droplets'),
    Eye: _createIcon('Eye'),
    EyeOff: _createIcon('EyeOff'),
    FileText: _createIcon('FileText'),
    Filter: _createIcon('Filter'),
    Layers: _createIcon('Layers'),
    MapPin: _createIcon('MapPin'),
    Sprout: _createIcon('Sprout'),
    User: _createIcon('User'),
    X: _createIcon('X'),
  };
});

// Mock @/lib/utils
vi.mock('@/lib/utils', () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(' '),
  formatDate: (date: string) => date,
  formatNumber: (num: number) => String(num),
  getSeverityColor: (severity: string) => {
    const colors: Record<string, string> = {
      low: 'text-green-600 bg-green-100',
      medium: 'text-yellow-600 bg-yellow-100',
      high: 'text-orange-600 bg-orange-100',
      critical: 'text-red-600 bg-red-100',
    };
    return colors[severity] || 'text-gray-600 bg-gray-100';
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
}));

// Mock @/components/ui/StatCard
vi.mock('@/components/ui/StatCard', () => ({
  default: ({ title, value, suffix }: { title: string; value: string | number; suffix?: string }) =>
    React.createElement(
      'div',
      { 'data-testid': 'stat-card' },
      React.createElement('span', null, title),
      React.createElement('span', null, String(value)),
      suffix && React.createElement('span', null, suffix)
    ),
}));

// Mock @/components/ui/AlertBadge
vi.mock('@/components/ui/AlertBadge', () => ({
  default: ({ severity }: { severity: string }) =>
    React.createElement('span', { 'data-testid': 'alert-badge' }, severity),
}));

// Import components after mocks
import MetricsGrid from '../MetricsGrid';
import AlertsPanel, { type Alert } from '../AlertsPanel';
import ActivityFeed, { type ActivityItem } from '../ActivityFeed';

// ═══════════════════════════════════════════════════════════════════════════
// MetricsGrid Tests | اختبارات شبكة المقاييس
// ═══════════════════════════════════════════════════════════════════════════

const MockIcon = (props: Record<string, unknown>) =>
  React.createElement('svg', { 'data-testid': 'metric-icon', ...props });

describe('MetricsGrid', () => {
  const sampleMetrics = [
    { title: 'المزارع النشطة', value: 125, icon: MockIcon },
    { title: 'الحقول', value: 350, icon: MockIcon },
    { title: 'المحاصيل', value: 28, icon: MockIcon },
    { title: 'المساحة الكلية', value: 1200, icon: MockIcon, suffix: 'هكتار' },
  ];

  it('renders all metrics', () => {
    render(<MetricsGrid metrics={sampleMetrics} />);
    const cards = screen.getAllByTestId('stat-card');
    expect(cards).toHaveLength(4);
  });

  it('displays metric titles', () => {
    render(<MetricsGrid metrics={sampleMetrics} />);
    expect(screen.getByText('المزارع النشطة')).toBeInTheDocument();
    expect(screen.getByText('الحقول')).toBeInTheDocument();
    expect(screen.getByText('المحاصيل')).toBeInTheDocument();
    expect(screen.getByText('المساحة الكلية')).toBeInTheDocument();
  });

  it('displays metric values', () => {
    render(<MetricsGrid metrics={sampleMetrics} />);
    expect(screen.getByText('125')).toBeInTheDocument();
    expect(screen.getByText('350')).toBeInTheDocument();
  });

  it('renders with suffix', () => {
    render(<MetricsGrid metrics={sampleMetrics} />);
    expect(screen.getByText('هكتار')).toBeInTheDocument();
  });

  it('applies custom columns class', () => {
    const { container } = render(<MetricsGrid metrics={sampleMetrics} columns={3} />);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('lg:grid-cols-3');
  });

  it('defaults to 4 columns', () => {
    const { container } = render(<MetricsGrid metrics={sampleMetrics} />);
    const grid = container.firstChild as HTMLElement;
    expect(grid.className).toContain('lg:grid-cols-4');
  });

  it('renders empty grid when no metrics', () => {
    render(<MetricsGrid metrics={[]} />);
    const cards = screen.queryAllByTestId('stat-card');
    expect(cards).toHaveLength(0);
  });

  it('renders with trend data', () => {
    const metricsWithTrend = [
      {
        title: 'الإنتاج',
        value: 1000,
        icon: MockIcon,
        trend: { value: 12.5, isPositive: true },
      },
    ];
    render(<MetricsGrid metrics={metricsWithTrend} />);
    expect(screen.getByText('الإنتاج')).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// AlertsPanel Tests | اختبارات لوحة التنبيهات
// ═══════════════════════════════════════════════════════════════════════════

describe('AlertsPanel', () => {
  const sampleAlerts: Alert[] = [
    {
      id: 'a-1',
      type: 'pest',
      severity: 'critical',
      title: 'RPW Detected',
      titleAr: 'كشف سوسة النخيل',
      message: 'Red Palm Weevil detected',
      messageAr: 'تم كشف سوسة النخيل الحمراء',
      farmName: 'مزرعة 1',
      timestamp: '2026-01-15T10:00:00Z',
      read: false,
    },
    {
      id: 'a-2',
      type: 'weather',
      severity: 'medium',
      title: 'Rain Expected',
      titleAr: 'أمطار متوقعة',
      message: 'Rain expected tomorrow',
      messageAr: 'أمطار متوقعة غداً',
      timestamp: '2026-01-15T09:00:00Z',
      read: true,
    },
    {
      id: 'a-3',
      type: 'irrigation',
      severity: 'low',
      title: 'Irrigation Complete',
      titleAr: 'اكتمال الري',
      message: 'Irrigation cycle finished',
      messageAr: 'دورة الري اكتملت',
      timestamp: '2026-01-15T08:00:00Z',
      read: true,
    },
  ];

  it('renders alert titles in Arabic', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('كشف سوسة النخيل')).toBeInTheDocument();
    expect(screen.getByText('أمطار متوقعة')).toBeInTheDocument();
  });

  it('renders alert messages in Arabic', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('تم كشف سوسة النخيل الحمراء')).toBeInTheDocument();
  });

  it('shows header with title', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('التنبيهات')).toBeInTheDocument();
  });

  it('shows unread count badge', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    // 1 unread alert
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('shows filter buttons when showFilters is true', () => {
    render(<AlertsPanel alerts={sampleAlerts} showFilters={true} />);
    expect(screen.getByText(/الكل/)).toBeInTheDocument();
    expect(screen.getByText(/حرجة/)).toBeInTheDocument();
    expect(screen.getByText(/غير مقروءة/)).toBeInTheDocument();
  });

  it('hides filter buttons when showFilters is false', () => {
    render(<AlertsPanel alerts={sampleAlerts} showFilters={false} />);
    expect(screen.queryByText(/حرجة \(/)).not.toBeInTheDocument();
  });

  it('filters by critical severity', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);

    const criticalButton = screen.getByText(/حرجة/);
    fireEvent.click(criticalButton);

    // Only critical alert should show
    expect(screen.getByText('كشف سوسة النخيل')).toBeInTheDocument();
    expect(screen.queryByText('أمطار متوقعة')).not.toBeInTheDocument();
  });

  it('filters by unread status', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);

    const unreadButton = screen.getByText(/غير مقروءة/);
    fireEvent.click(unreadButton);

    // Only unread alert should show
    expect(screen.getByText('كشف سوسة النخيل')).toBeInTheDocument();
    expect(screen.queryByText('أمطار متوقعة')).not.toBeInTheDocument();
  });

  it('shows empty state when no alerts', () => {
    render(<AlertsPanel alerts={[]} />);
    expect(screen.getByText('لا توجد تنبيهات')).toBeInTheDocument();
  });

  it('renders alert severity badges', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    const badges = screen.getAllByTestId('alert-badge');
    expect(badges.length).toBeGreaterThanOrEqual(1);
  });

  it('calls onMarkAsRead when mark as read button is clicked', () => {
    const onMarkAsRead = vi.fn();
    render(<AlertsPanel alerts={sampleAlerts} onMarkAsRead={onMarkAsRead} />);

    const markReadButton = screen.getByLabelText('وضع علامة كمقروء');
    fireEvent.click(markReadButton);

    expect(onMarkAsRead).toHaveBeenCalledWith('a-1');
  });

  it('calls onDismiss when dismiss button is clicked', () => {
    const onDismiss = vi.fn();
    render(<AlertsPanel alerts={sampleAlerts} onDismiss={onDismiss} />);

    const dismissButtons = screen.getAllByLabelText('إخفاء التنبيه');
    fireEvent.click(dismissButtons[0]);

    expect(onDismiss).toHaveBeenCalledWith('a-1');
  });

  it('respects maxItems prop', () => {
    render(<AlertsPanel alerts={sampleAlerts} maxItems={1} />);
    // Only 1 alert should render
    expect(screen.getByText('كشف سوسة النخيل')).toBeInTheDocument();
    expect(screen.queryByText('اكتمال الري')).not.toBeInTheDocument();
  });

  it('shows farm name when provided', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('مزرعة 1')).toBeInTheDocument();
  });

  it('displays alert type labels', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('آفة')).toBeInTheDocument();
    expect(screen.getByText('طقس')).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// ActivityFeed Tests | اختبارات تدفق النشاطات
// ═══════════════════════════════════════════════════════════════════════════

describe('ActivityFeed', () => {
  const sampleActivities: ActivityItem[] = [
    {
      id: 'act-1',
      type: 'diagnosis',
      action: 'Disease Diagnosed',
      actionAr: 'تم تشخيص المرض',
      description: 'Wheat rust detected in Field A',
      descriptionAr: 'تم اكتشاف صدأ القمح في حقل أ',
      userName: 'أحمد',
      farmName: 'مزرعة 1',
      timestamp: '2026-01-15T10:00:00Z',
    },
    {
      id: 'act-2',
      type: 'irrigation',
      action: 'Irrigation Started',
      actionAr: 'بدأ الري',
      description: 'Irrigation cycle started for Field B',
      descriptionAr: 'بدأت دورة الري لحقل ب',
      userName: 'خالد',
      timestamp: '2026-01-15T09:00:00Z',
    },
    {
      id: 'act-3',
      type: 'task',
      action: 'Task Completed',
      actionAr: 'اكتملت المهمة',
      description: 'Fertilization task completed',
      descriptionAr: 'اكتملت مهمة التسميد',
      timestamp: '2026-01-15T08:00:00Z',
      actionUrl: '/tasks/t-1',
    },
  ];

  it('renders activity actions in Arabic', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('تم تشخيص المرض')).toBeInTheDocument();
    expect(screen.getByText('بدأ الري')).toBeInTheDocument();
  });

  it('renders activity descriptions in Arabic', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('تم اكتشاف صدأ القمح في حقل أ')).toBeInTheDocument();
  });

  it('shows header with title', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('النشاطات الأخيرة')).toBeInTheDocument();
  });

  it('shows filter dropdown when showFilters is true', () => {
    render(<ActivityFeed activities={sampleActivities} showFilters={true} />);
    expect(screen.getByLabelText('تصفية النشاطات حسب النوع')).toBeInTheDocument();
  });

  it('hides filter when showFilters is false', () => {
    render(<ActivityFeed activities={sampleActivities} showFilters={false} />);
    expect(screen.queryByLabelText('تصفية النشاطات حسب النوع')).not.toBeInTheDocument();
  });

  it('filters activities by type', () => {
    render(<ActivityFeed activities={sampleActivities} />);

    const filterSelect = screen.getByLabelText('تصفية النشاطات حسب النوع');
    fireEvent.change(filterSelect, { target: { value: 'diagnosis' } });

    expect(screen.getByText('تم تشخيص المرض')).toBeInTheDocument();
    expect(screen.queryByText('بدأ الري')).not.toBeInTheDocument();
  });

  it('shows empty state when no activities', () => {
    render(<ActivityFeed activities={[]} />);
    expect(screen.getByText('لا توجد نشاطات')).toBeInTheDocument();
  });

  it('displays user name when provided', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('أحمد')).toBeInTheDocument();
    expect(screen.getByText('خالد')).toBeInTheDocument();
  });

  it('displays farm name when provided', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('مزرعة 1')).toBeInTheDocument();
  });

  it('shows activity type labels', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('تشخيص')).toBeInTheDocument();
    // "ري" appears in both the type label and description text, so use getAllByText
    expect(screen.getAllByText(/^ري$/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('مهمة')).toBeInTheDocument();
  });

  it('renders action links when actionUrl is provided', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    const links = screen.getAllByText('عرض ←');
    expect(links.length).toBeGreaterThanOrEqual(1);
  });

  it('respects maxItems prop', () => {
    render(<ActivityFeed activities={sampleActivities} maxItems={1} />);
    expect(screen.getByText('تم تشخيص المرض')).toBeInTheDocument();
    // Load more button should appear
    expect(screen.getByText('تحميل المزيد ←')).toBeInTheDocument();
  });

  it('loads more items on button click', () => {
    render(<ActivityFeed activities={sampleActivities} maxItems={1} />);

    const loadMore = screen.getByText('تحميل المزيد ←');
    fireEvent.click(loadMore);

    // Should show more activities now
    expect(screen.getByText('بدأ الري')).toBeInTheDocument();
  });
});
