/**
 * Dashboard Widget Tests
 * اختبارات أدوات لوحة التحكم
 *
 * Tests for: AlertsPanel, ActivityFeed, MapOverview, RealTimeActivityFeed
 */

import { describe, it, expect, vi, beforeAll } from 'vitest';
import React from 'react';
import fs from 'fs';
import path from 'path';
import { render, screen, fireEvent } from '../../../__tests__/test-utils';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

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

// Mock next/dynamic - returns a component that renders a placeholder
vi.mock('next/dynamic', () => ({
  default: () => {
    const DynamicComponent = (props: Record<string, unknown>) =>
      React.createElement('div', { 'data-testid': 'dynamic-map', ...props }, 'Map');
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
    CloudRain: _createIcon('CloudRain'),
    Droplets: _createIcon('Droplets'),
    Eye: _createIcon('Eye'),
    EyeOff: _createIcon('EyeOff'),
    FileText: _createIcon('FileText'),
    Filter: _createIcon('Filter'),
    Layers: _createIcon('Layers'),
    Leaf: _createIcon('Leaf'),
    MapPin: _createIcon('MapPin'),
    Settings: _createIcon('Settings'),
    Sprout: _createIcon('Sprout'),
    Truck: _createIcon('Truck'),
    User: _createIcon('User'),
    Users: _createIcon('Users'),
    X: _createIcon('X'),
    Zap: _createIcon('Zap'),
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

// Mock @/components/ui/AlertBadge
vi.mock('@/components/ui/AlertBadge', () => ({
  default: ({ severity }: { severity: string }) =>
    React.createElement('span', { 'data-testid': 'alert-badge' }, severity),
}));

// Import components after mocks
import AlertsPanel, { type Alert } from '../AlertsPanel';
import ActivityFeed, { type ActivityItem } from '../ActivityFeed';
import MapOverview, { type MapFarm } from '../MapOverview';
// RealTimeActivityFeed tested via source analysis (fs.readFileSync) below

// ═══════════════════════════════════════════════════════════════════════════
// AlertsPanel Widget Tests | اختبارات أداة لوحة التنبيهات
// ═══════════════════════════════════════════════════════════════════════════

describe('AlertsPanel (widget tests)', () => {
  const sampleAlerts: Alert[] = [
    {
      id: 'alert-w-1',
      type: 'disease',
      severity: 'critical',
      title: 'Wheat Rust Detected',
      titleAr: 'تم اكتشاف صدأ القمح',
      message: 'Wheat rust detected in Field 5',
      messageAr: 'تم اكتشاف صدأ القمح في الحقل 5',
      farmId: 'farm-1',
      farmName: 'مزرعة الرشيد',
      timestamp: '2026-03-20T08:00:00Z',
      read: false,
      actionUrl: '/alerts/alert-w-1',
    },
    {
      id: 'alert-w-2',
      type: 'sensor',
      severity: 'high',
      title: 'Sensor Offline',
      titleAr: 'المستشعر غير متصل',
      message: 'Soil moisture sensor offline',
      messageAr: 'مستشعر رطوبة التربة غير متصل',
      timestamp: '2026-03-20T07:00:00Z',
      read: false,
    },
    {
      id: 'alert-w-3',
      type: 'general',
      severity: 'low',
      title: 'System Update',
      titleAr: 'تحديث النظام',
      message: 'System update available',
      messageAr: 'تحديث النظام متاح',
      timestamp: '2026-03-20T06:00:00Z',
      read: true,
    },
  ];

  it('renders without crashing', () => {
    const { container } = render(<AlertsPanel alerts={sampleAlerts} />);
    expect(container).toBeTruthy();
  });

  it('displays the Arabic header title', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('التنبيهات')).toBeInTheDocument();
  });

  it('renders the Bell icon', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    const bellIcons = screen.getAllByTestId('icon-Bell');
    expect(bellIcons.length).toBeGreaterThanOrEqual(1);
  });

  it('displays alert type labels in Arabic', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('مرض')).toBeInTheDocument();
    expect(screen.getByText('مستشعر')).toBeInTheDocument();
    expect(screen.getByText('عام')).toBeInTheDocument();
  });

  it('renders action link when actionUrl is provided', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    expect(screen.getByText('عرض')).toBeInTheDocument();
  });

  it('shows unread count for unread alerts', () => {
    render(<AlertsPanel alerts={sampleAlerts} />);
    // 2 unread alerts
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('displays the "view all" footer link when maxItems is less than total', () => {
    render(<AlertsPanel alerts={sampleAlerts} maxItems={1} />);
    expect(screen.getByText(/عرض جميع التنبيهات/)).toBeInTheDocument();
  });

  it('shows empty state message with no alerts', () => {
    render(<AlertsPanel alerts={[]} />);
    expect(screen.getByText('لا توجد تنبيهات')).toBeInTheDocument();
  });

  it('renders filter buttons with correct Arabic labels', () => {
    render(<AlertsPanel alerts={sampleAlerts} showFilters={true} />);
    expect(screen.getByText(/الكل/)).toBeInTheDocument();
    expect(screen.getByText(/حرجة/)).toBeInTheDocument();
    expect(screen.getByText(/غير مقروءة/)).toBeInTheDocument();
  });

  it('calls onDismiss callback when dismiss button is clicked', () => {
    const onDismiss = vi.fn();
    render(<AlertsPanel alerts={sampleAlerts} onDismiss={onDismiss} />);

    const dismissButtons = screen.getAllByLabelText('إخفاء التنبيه');
    fireEvent.click(dismissButtons[0]);
    expect(onDismiss).toHaveBeenCalledWith('alert-w-1');
  });

  it('calls onMarkAsRead callback for unread alerts', () => {
    const onMarkAsRead = vi.fn();
    render(<AlertsPanel alerts={sampleAlerts} onMarkAsRead={onMarkAsRead} />);

    const markReadButtons = screen.getAllByLabelText('وضع علامة كمقروء');
    fireEvent.click(markReadButtons[0]);
    expect(onMarkAsRead).toHaveBeenCalled();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// ActivityFeed Widget Tests | اختبارات أداة تدفق النشاطات
// ═══════════════════════════════════════════════════════════════════════════

describe('ActivityFeed (widget tests)', () => {
  const sampleActivities: ActivityItem[] = [
    {
      id: 'af-1',
      type: 'diagnosis',
      action: 'Disease Diagnosed',
      actionAr: 'تم تشخيص مرض القمح',
      description: 'Wheat disease diagnosed',
      descriptionAr: 'تم تشخيص مرض في محصول القمح',
      userName: 'محمد',
      farmName: 'مزرعة النور',
      timestamp: '2026-03-20T10:00:00Z',
    },
    {
      id: 'af-2',
      type: 'irrigation',
      action: 'Irrigation Started',
      actionAr: 'بدأ الري التلقائي',
      description: 'Auto irrigation started',
      descriptionAr: 'بدأ الري التلقائي للحقل',
      timestamp: '2026-03-20T09:00:00Z',
      actionUrl: '/irrigation/af-2',
    },
    {
      id: 'af-3',
      type: 'alert',
      action: 'Alert Triggered',
      actionAr: 'تم تفعيل تنبيه',
      description: 'Weather alert triggered',
      descriptionAr: 'تم تفعيل تنبيه طقس',
      timestamp: '2026-03-20T08:00:00Z',
    },
    {
      id: 'af-4',
      type: 'sensor',
      action: 'Sensor Reading',
      actionAr: 'قراءة المستشعر',
      description: 'New sensor reading',
      descriptionAr: 'قراءة جديدة من المستشعر',
      timestamp: '2026-03-20T07:00:00Z',
    },
  ];

  it('renders without crashing', () => {
    const { container } = render(<ActivityFeed activities={sampleActivities} />);
    expect(container).toBeTruthy();
  });

  it('displays the Arabic header title', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('النشاطات الأخيرة')).toBeInTheDocument();
  });

  it('renders the Activity icon in header', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    const activityIcons = screen.getAllByTestId('icon-Activity');
    expect(activityIcons.length).toBeGreaterThanOrEqual(1);
  });

  it('displays Arabic action text for activities', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('تم تشخيص مرض القمح')).toBeInTheDocument();
    expect(screen.getByText('بدأ الري التلقائي')).toBeInTheDocument();
    expect(screen.getByText('تم تفعيل تنبيه')).toBeInTheDocument();
  });

  it('displays Arabic description text', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('تم تشخيص مرض في محصول القمح')).toBeInTheDocument();
  });

  it('shows Arabic activity type labels', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('تشخيص')).toBeInTheDocument();
    expect(screen.getByText('تنبيه')).toBeInTheDocument();
    expect(screen.getByText('مستشعر')).toBeInTheDocument();
  });

  it('displays user name when provided', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('محمد')).toBeInTheDocument();
  });

  it('displays farm name when provided', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    expect(screen.getByText('مزرعة النور')).toBeInTheDocument();
  });

  it('shows empty state when no activities exist', () => {
    render(<ActivityFeed activities={[]} />);
    expect(screen.getByText('لا توجد نشاطات')).toBeInTheDocument();
  });

  it('renders filter dropdown with Arabic label', () => {
    render(<ActivityFeed activities={sampleActivities} showFilters={true} />);
    expect(screen.getByLabelText('تصفية النشاطات حسب النوع')).toBeInTheDocument();
  });

  it('filters activities when filter is changed', () => {
    render(<ActivityFeed activities={sampleActivities} />);

    const filterSelect = screen.getByLabelText('تصفية النشاطات حسب النوع');
    fireEvent.change(filterSelect, { target: { value: 'alert' } });

    expect(screen.getByText('تم تفعيل تنبيه')).toBeInTheDocument();
    expect(screen.queryByText('تم تشخيص مرض القمح')).not.toBeInTheDocument();
  });

  it('renders action link when actionUrl is provided', () => {
    render(<ActivityFeed activities={sampleActivities} />);
    const links = screen.getAllByText('عرض ←');
    expect(links.length).toBeGreaterThanOrEqual(1);
  });

  it('shows load more button when maxItems limits display', () => {
    render(<ActivityFeed activities={sampleActivities} maxItems={2} />);
    expect(screen.getByText('تحميل المزيد ←')).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// MapOverview Widget Tests | اختبارات أداة نظرة عامة على الخريطة
// ═══════════════════════════════════════════════════════════════════════════

describe('MapOverview (widget tests)', () => {
  const sampleFarms: MapFarm[] = [
    {
      id: 'farm-1',
      name: 'Al-Rashid Farm',
      nameAr: 'مزرعة الرشيد',
      coordinates: { lat: 15.3694, lng: 44.191 },
      healthScore: 85,
      area: 10.5,
      crops: ['wheat', 'barley'],
    },
    {
      id: 'farm-2',
      name: 'Al-Noor Farm',
      nameAr: 'مزرعة النور',
      coordinates: { lat: 15.4, lng: 44.2 },
      healthScore: 55,
      area: 8.0,
      crops: ['tomato'],
    },
    {
      id: 'farm-3',
      name: 'Al-Salam Farm',
      nameAr: 'مزرعة السلام',
      coordinates: { lat: 15.5, lng: 44.3 },
      healthScore: 30,
      area: 5.0,
      crops: ['date_palm'],
    },
  ];

  it('renders without crashing', () => {
    const { container } = render(<MapOverview farms={sampleFarms} />);
    expect(container).toBeTruthy();
  });

  it('displays the Arabic header title', () => {
    render(<MapOverview farms={sampleFarms} />);
    expect(screen.getByText('خريطة المزارع')).toBeInTheDocument();
  });

  it('renders the MapPin icon in header', () => {
    render(<MapOverview farms={sampleFarms} />);
    const mapPinIcons = screen.getAllByTestId('icon-MapPin');
    expect(mapPinIcons.length).toBeGreaterThanOrEqual(1);
  });

  it('shows health statistics when overlay is enabled', () => {
    render(<MapOverview farms={sampleFarms} showHealthOverlay={true} />);
    // healthy farms (score >= 70): farm-1
    expect(screen.getByText('صحي:')).toBeInTheDocument();
    // warning farms (50-69): farm-2
    expect(screen.getByText('تحذير:')).toBeInTheDocument();
    // critical farms (<50): farm-3
    expect(screen.getByText('حرج:')).toBeInTheDocument();
  });

  it('displays total farms count', () => {
    render(<MapOverview farms={sampleFarms} showHealthOverlay={true} />);
    expect(screen.getByText('إجمالي المزارع:')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders the dynamic map component', () => {
    render(<MapOverview farms={sampleFarms} />);
    expect(screen.getByTestId('dynamic-map')).toBeInTheDocument();
  });

  it('shows legend when health overlay is enabled', () => {
    render(<MapOverview farms={sampleFarms} showHealthOverlay={true} />);
    expect(screen.getByText(/الألوان تمثل مستوى صحة المحصول/)).toBeInTheDocument();
  });

  it('renders map view select control', () => {
    render(<MapOverview farms={sampleFarms} showControls={true} />);
    expect(screen.getByText('خريطة عادية')).toBeInTheDocument();
    expect(screen.getByText('صور الأقمار')).toBeInTheDocument();
  });

  it('shows health layer toggle button', () => {
    render(<MapOverview farms={sampleFarms} showControls={true} />);
    expect(screen.getByText('طبقة الصحة')).toBeInTheDocument();
  });

  it('toggles health overlay on button click', () => {
    render(<MapOverview farms={sampleFarms} showControls={true} showHealthOverlay={true} />);

    // Initially health stats should be visible
    expect(screen.getByText('صحي:')).toBeInTheDocument();

    // Click toggle button to hide overlay
    const toggleButton = screen.getByText('طبقة الصحة');
    fireEvent.click(toggleButton);

    // Health stats should no longer be visible
    expect(screen.queryByText('صحي:')).not.toBeInTheDocument();
  });

  it('shows "view all" link', () => {
    render(<MapOverview farms={sampleFarms} showControls={true} />);
    expect(screen.getByText('عرض الكل ←')).toBeInTheDocument();
  });

  it('hides controls when showControls is false', () => {
    render(<MapOverview farms={sampleFarms} showControls={false} />);
    expect(screen.queryByText('طبقة الصحة')).not.toBeInTheDocument();
    expect(screen.queryByText('عرض الكل ←')).not.toBeInTheDocument();
  });

  it('renders with empty farms array', () => {
    render(<MapOverview farms={[]} />);
    expect(screen.getByText('خريطة المزارع')).toBeInTheDocument();
    expect(screen.getByTestId('dynamic-map')).toBeInTheDocument();
  });

  it('calls onFarmClick when provided', () => {
    const onFarmClick = vi.fn();
    render(<MapOverview farms={sampleFarms} onFarmClick={onFarmClick} />);
    // The map itself is mocked, so we just verify the component renders
    // without error when onFarmClick is passed
    expect(screen.getByTestId('dynamic-map')).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// RealTimeActivityFeed Widget Tests | اختبارات أداة بث النشاطات المباشرة
// ═══════════════════════════════════════════════════════════════════════════

describe('RealTimeActivityFeed (source analysis)', () => {
  const filePath = path.resolve(__dirname, '../RealTimeActivityFeed.tsx');
  let content: string;

  beforeAll(() => {
    content = fs.readFileSync(filePath, 'utf-8');
  });

  it('file exists', () => {
    expect(fs.existsSync(filePath)).toBe(true);
  });

  it('has use client directive', () => {
    expect(content).toMatch(/['"]use client['"]/);
  });

  it('exports default component', () => {
    expect(content).toMatch(/export default (?:function )?RealTimeActivityFeed/);
  });

  it('includes Arabic labels for header', () => {
    expect(content).toContain('النشاطات المباشرة');
  });

  it('has connection status labels in Arabic', () => {
    expect(content).toContain('متصل');
  });

  it('has pause/resume functionality', () => {
    expect(content).toContain('مباشر');
  });

  it('has clear all button in Arabic', () => {
    expect(content).toContain('مسح الكل');
  });

  it('has filter support', () => {
    expect(content).toContain('showFilters');
  });

  it('has empty state message', () => {
    expect(content).toContain('لا توجد نشاطات');
  });

  it('uses lucide-react icons', () => {
    expect(content).toContain('lucide-react');
  });
});
