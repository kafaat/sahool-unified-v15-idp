/**
 * Home Components Tests - Dashboard Widgets
 * اختبارات مكونات لوحة التحكم الرئيسية
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// ─── Mocks ────────────────────────────────────────────────────────────────────

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

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/dashboard',
}));

vi.mock('lucide-react', () => {
  const _React = require('react');
  const _mk = (name: string) => {
    const C = (props: Record<string, unknown>) =>
      _React.createElement('svg', { 'data-testid': `icon-${name}`, ...props });
    C.displayName = name;
    return C;
  };
  return {
    __esModule: true,
    Cloud: _mk('Cloud'),
    CloudRain: _mk('CloudRain'),
    Sun: _mk('Sun'),
    Wind: _mk('Wind'),
    Droplets: _mk('Droplets'),
    RefreshCw: _mk('RefreshCw'),
    Plus: _mk('Plus'),
    MapPin: _mk('MapPin'),
    ListTodo: _mk('ListTodo'),
    CloudSun: _mk('CloudSun'),
    FileText: _mk('FileText'),
    Settings: _mk('Settings'),
    Activity: _mk('Activity'),
    Clock: _mk('Clock'),
    ClipboardList: _mk('ClipboardList'),
    AlertTriangle: _mk('AlertTriangle'),
    Sprout: _mk('Sprout'),
    CheckCircle2: _mk('CheckCircle2'),
    Calendar: _mk('Calendar'),
    ArrowLeft: _mk('ArrowLeft'),
  };
});

// ─── WeatherWidget Tests ──────────────────────────────────────────────────────

const mockRefetch = vi.fn().mockResolvedValue({});

vi.mock('../../hooks/useWeather', () => ({
  useWeather: vi.fn(),
}));

vi.mock('../../hooks/useRecentActivity', () => ({
  useRecentActivity: vi.fn(),
}));

vi.mock('../../hooks/useUpcomingTasks', () => ({
  useUpcomingTasks: vi.fn(),
}));

import { useWeather } from '../../hooks/useWeather';
import { useRecentActivity } from '../../hooks/useRecentActivity';
import { useUpcomingTasks } from '../../hooks/useUpcomingTasks';
import { WeatherWidget } from '../WeatherWidget';
import { QuickActions } from '../QuickActions';
import { RecentActivity } from '../RecentActivity';
import { TasksSummary } from '../TasksSummary';

describe('WeatherWidget', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading state', () => {
    vi.mocked(useWeather).mockReturnValue({
      data: undefined,
      isLoading: true,
      dataUpdatedAt: 0,
      refetch: mockRefetch,
    } as ReturnType<typeof useWeather>);

    render(<WeatherWidget />);
    expect(screen.getByText('جاري التحميل...')).toBeInTheDocument();
  });

  it('shows empty state when no weather data', () => {
    vi.mocked(useWeather).mockReturnValue({
      data: undefined,
      isLoading: false,
      dataUpdatedAt: 0,
      refetch: mockRefetch,
    } as ReturnType<typeof useWeather>);

    render(<WeatherWidget />);
    expect(screen.getByText('بيانات الطقس غير متوفرة')).toBeInTheDocument();
  });

  it('renders weather data correctly', () => {
    vi.mocked(useWeather).mockReturnValue({
      data: {
        temperature: 28,
        humidity: 45,
        windSpeed: 12,
        condition: 'Clear',
        conditionAr: 'صافي',
        location: 'الرياض',
      },
      isLoading: false,
      dataUpdatedAt: Date.now(),
      refetch: mockRefetch,
    } as ReturnType<typeof useWeather>);

    render(<WeatherWidget />);
    expect(screen.getByText('28°C')).toBeInTheDocument();
    expect(screen.getByText('صافي')).toBeInTheDocument();
    expect(screen.getByText('45%')).toBeInTheDocument();
    expect(screen.getByText('12 km/h')).toBeInTheDocument();
    expect(screen.getByText('الرياض')).toBeInTheDocument();
  });

  it('renders header titles', () => {
    vi.mocked(useWeather).mockReturnValue({
      data: {
        temperature: 28,
        humidity: 45,
        windSpeed: 12,
        condition: 'Clear',
      },
      isLoading: false,
      dataUpdatedAt: 0,
      refetch: mockRefetch,
    } as ReturnType<typeof useWeather>);

    render(<WeatherWidget />);
    expect(screen.getByText('الطقس الحالي')).toBeInTheDocument();
    expect(screen.getByText('Current Weather')).toBeInTheDocument();
  });

  it('has refresh button with correct aria-label', () => {
    vi.mocked(useWeather).mockReturnValue({
      data: {
        temperature: 28,
        humidity: 45,
        windSpeed: 12,
        condition: 'Clear',
      },
      isLoading: false,
      dataUpdatedAt: 0,
      refetch: mockRefetch,
    } as ReturnType<typeof useWeather>);

    render(<WeatherWidget />);
    const refreshBtn = screen.getByLabelText('تحديث الطقس');
    expect(refreshBtn).toBeInTheDocument();
  });
});

// ─── QuickActions Tests ───────────────────────────────────────────────────────

describe('QuickActions', () => {
  it('renders all 6 action buttons', () => {
    render(<QuickActions />);
    expect(screen.getByText('إضافة حقل')).toBeInTheDocument();
    expect(screen.getByText('مهمة جديدة')).toBeInTheDocument();
    expect(screen.getByText('الطقس')).toBeInTheDocument();
    expect(screen.getByText('التقارير')).toBeInTheDocument();
    expect(screen.getByText('جميع المهام')).toBeInTheDocument();
    expect(screen.getByText('الإعدادات')).toBeInTheDocument();
  });

  it('renders English labels', () => {
    render(<QuickActions />);
    expect(screen.getByText('Add Field')).toBeInTheDocument();
    expect(screen.getByText('New Task')).toBeInTheDocument();
    expect(screen.getByText('Weather')).toBeInTheDocument();
    expect(screen.getByText('Reports')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders header', () => {
    render(<QuickActions />);
    expect(screen.getByText('الإجراءات السريعة')).toBeInTheDocument();
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
  });

  it('renders correct links', () => {
    render(<QuickActions />);
    const addFieldLink = screen.getByText('إضافة حقل').closest('a');
    expect(addFieldLink).toHaveAttribute('href', '/fields?action=new');

    const tasksLink = screen.getByText('مهمة جديدة').closest('a');
    expect(tasksLink).toHaveAttribute('href', '/tasks?action=new');

    const settingsLink = screen.getByText('الإعدادات').closest('a');
    expect(settingsLink).toHaveAttribute('href', '/settings');
  });
});

// ─── RecentActivity Tests ─────────────────────────────────────────────────────

describe('RecentActivity', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading skeleton', () => {
    vi.mocked(useRecentActivity).mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useRecentActivity>);

    render(<RecentActivity />);
    expect(screen.getByText('النشاط الأخير')).toBeInTheDocument();
  });

  it('shows empty state when no activities', () => {
    vi.mocked(useRecentActivity).mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useRecentActivity>);

    render(<RecentActivity />);
    expect(screen.getByText('لا يوجد نشاط حديث')).toBeInTheDocument();
    expect(screen.getByText('No recent activity')).toBeInTheDocument();
  });

  it('renders activity items', () => {
    vi.mocked(useRecentActivity).mockReturnValue({
      data: [
        {
          id: '1',
          type: 'task',
          title: 'Irrigation check',
          titleAr: 'فحص الري',
          description: 'Field 001',
          descriptionAr: 'الحقل 001',
          timestamp: '2026-01-20T10:30:00Z',
        },
        {
          id: '2',
          type: 'alert',
          title: 'Temperature warning',
          titleAr: 'تحذير حرارة',
          description: 'Above threshold',
          descriptionAr: 'أعلى من الحد',
          timestamp: '2026-01-20T09:00:00Z',
        },
      ],
      isLoading: false,
    } as ReturnType<typeof useRecentActivity>);

    render(<RecentActivity />);
    expect(screen.getByText('فحص الري')).toBeInTheDocument();
    expect(screen.getByText('تحذير حرارة')).toBeInTheDocument();
    expect(screen.getByText('الحقل 001')).toBeInTheDocument();
  });

  it('renders bilingual header', () => {
    vi.mocked(useRecentActivity).mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useRecentActivity>);

    render(<RecentActivity />);
    expect(screen.getByText('النشاط الأخير')).toBeInTheDocument();
    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
  });
});

// ─── TasksSummary Tests ───────────────────────────────────────────────────────

// TasksSummary uses useCompleteTask/useUpdateTaskStatus which need QueryClientProvider
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('@/features/tasks/hooks/useTasks', () => ({
  useCompleteTask: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateTaskStatus: () => ({ mutate: vi.fn(), isPending: false }),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe('TasksSummary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading skeleton', () => {
    vi.mocked(useUpcomingTasks).mockReturnValue({
      data: undefined,
      isLoading: true,
    } as ReturnType<typeof useUpcomingTasks>);

    render(<TasksSummary />, { wrapper: createWrapper() });
    expect(screen.getByText('المهام القادمة')).toBeInTheDocument();
  });

  it('shows empty state when no tasks', () => {
    vi.mocked(useUpcomingTasks).mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useUpcomingTasks>);

    render(<TasksSummary />, { wrapper: createWrapper() });
    expect(screen.getByText('لا توجد مهام قادمة')).toBeInTheDocument();
    expect(screen.getByText('No upcoming tasks')).toBeInTheDocument();
  });

  it('renders task items with priority labels', () => {
    vi.mocked(useUpcomingTasks).mockReturnValue({
      data: [
        {
          id: 't1',
          title: 'Irrigate wheat',
          titleAr: 'ري القمح',
          dueDate: '2026-03-20',
          priority: 'high',
          status: 'pending',
        },
        {
          id: 't2',
          title: 'Apply fertilizer',
          titleAr: 'تسميد الأرض',
          dueDate: '2026-03-25',
          priority: 'medium',
          status: 'pending',
        },
        {
          id: 't3',
          title: 'Inspect field',
          titleAr: 'فحص الحقل',
          dueDate: '2026-04-01',
          priority: 'low',
          status: 'pending',
        },
      ],
      isLoading: false,
    } as ReturnType<typeof useUpcomingTasks>);

    render(<TasksSummary />, { wrapper: createWrapper() });
    expect(screen.getByText('ري القمح')).toBeInTheDocument();
    expect(screen.getByText('تسميد الأرض')).toBeInTheDocument();
    expect(screen.getByText('فحص الحقل')).toBeInTheDocument();
    expect(screen.getByText('عالية')).toBeInTheDocument();
    expect(screen.getByText('متوسطة')).toBeInTheDocument();
    expect(screen.getByText('منخفضة')).toBeInTheDocument();
  });

  it('toggles task completion on click', () => {
    vi.mocked(useUpcomingTasks).mockReturnValue({
      data: [
        {
          id: 't1',
          title: 'Irrigate wheat',
          titleAr: 'ري القمح',
          dueDate: '2026-03-20',
          priority: 'high',
          status: 'pending',
        },
      ],
      isLoading: false,
    } as ReturnType<typeof useUpcomingTasks>);

    render(<TasksSummary />, { wrapper: createWrapper() });
    const completeBtn = screen.getByLabelText('إكمال المهمة');
    fireEvent.click(completeBtn);
    // After toggle, the aria-label should change
    expect(screen.getByLabelText('إلغاء إكمال المهمة')).toBeInTheDocument();
  });

  it("renders 'view all' link when tasks exist", () => {
    vi.mocked(useUpcomingTasks).mockReturnValue({
      data: [
        {
          id: 't1',
          title: 'Task 1',
          titleAr: 'مهمة 1',
          dueDate: '2026-03-20',
          priority: 'high',
          status: 'pending',
        },
      ],
      isLoading: false,
    } as ReturnType<typeof useUpcomingTasks>);

    render(<TasksSummary />, { wrapper: createWrapper() });
    expect(screen.getByText('عرض جميع المهام')).toBeInTheDocument();
    const link = screen.getByText('عرض جميع المهام').closest('a');
    expect(link).toHaveAttribute('href', '/tasks');
  });

  it('renders bilingual header', () => {
    vi.mocked(useUpcomingTasks).mockReturnValue({
      data: [],
      isLoading: false,
    } as ReturnType<typeof useUpcomingTasks>);

    render(<TasksSummary />, { wrapper: createWrapper() });
    expect(screen.getByText('المهام القادمة')).toBeInTheDocument();
    expect(screen.getByText('Upcoming Tasks')).toBeInTheDocument();
  });
});
