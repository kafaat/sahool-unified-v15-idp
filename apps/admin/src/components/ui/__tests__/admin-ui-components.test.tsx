/**
 * Comprehensive Admin UI Component Tests
 * اختبارات شاملة لمكونات واجهة المستخدم في لوحة التحكم
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// ─── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('next/navigation', () => ({
  usePathname: () => '/admin/dashboard',
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

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

vi.mock('lucide-react', () => {
  // NOTE: require() is intentional here — vi.mock factories are hoisted before imports,
  // so ES6 imports cannot be used; require() is the correct Vitest pattern.
  const _React = require('react');
  const _mk = (name: string) => {
    const C = (props: Record<string, unknown>) =>
      _React.createElement('svg', { 'data-testid': `icon-${name}`, ...props });
    C.displayName = name;
    return C;
  };
  return {
    __esModule: true,
    TrendingUp: _mk('TrendingUp'),
    TrendingDown: _mk('TrendingDown'),
    ArrowUp: _mk('ArrowUp'),
    ArrowDown: _mk('ArrowDown'),
    Activity: _mk('Activity'),
    ChevronRight: _mk('ChevronRight'),
    ChevronLeft: _mk('ChevronLeft'),
    Home: _mk('Home'),
    AlertTriangle: _mk('AlertTriangle'),
    CheckCircle: _mk('CheckCircle'),
    XCircle: _mk('XCircle'),
    Info: _mk('Info'),
    AlertCircle: _mk('AlertCircle'),
    Users: _mk('Users'),
    Search: _mk('Search'),
    Filter: _mk('Filter'),
    X: _mk('X'),
    Check: _mk('Check'),
    Download: _mk('Download'),
    Bell: _mk('Bell'),
    Settings: _mk('Settings'),
    MapPin: _mk('MapPin'),
    Calendar: _mk('Calendar'),
    Moon: _mk('Moon'),
    Sun: _mk('Sun'),
    Globe: _mk('Globe'),
    Layers: _mk('Layers'),
    BarChart2: _mk('BarChart2'),
    Leaf: _mk('Leaf'),
    ChevronDown: _mk('ChevronDown'),
  };
});

vi.mock('@/lib/utils', () => ({
  cn: (...inputs: (string | undefined | null | false)[]) => inputs.filter(Boolean).join(' '),
  formatNumber: (num: number) => num.toLocaleString(),
  formatDate: (date: string) => new Date(date).toLocaleDateString('ar-YE'),
  formatArea: (ha: number) => `${ha} هكتار`,
  getStatusColor: (status: string) => {
    const colors: Record<string, string> = {
      active: 'text-green-600 bg-green-100',
      inactive: 'text-red-600 bg-red-100',
      pending: 'text-yellow-600 bg-yellow-100',
      confirmed: 'text-blue-600 bg-blue-100',
      treated: 'text-green-600 bg-green-100',
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  },
  getStatusLabel: (status: string, locale: string = 'ar') => {
    const ar: Record<string, string> = {
      active: 'نشط',
      inactive: 'غير نشط',
      pending: 'قيد الانتظار',
      confirmed: 'مؤكد',
      treated: 'تمت المعالجة',
    };
    const en: Record<string, string> = {
      active: 'Active',
      inactive: 'Inactive',
      pending: 'Pending',
      confirmed: 'Confirmed',
      treated: 'Treated',
    };
    return locale === 'ar' ? ar[status] || status : en[status] || status;
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
  getSeverityLabel: (severity: string, locale: string = 'ar') => {
    const ar: Record<string, string> = {
      low: 'منخفض',
      medium: 'متوسط',
      high: 'مرتفع',
      critical: 'حرج',
    };
    const en: Record<string, string> = {
      low: 'Low',
      medium: 'Medium',
      high: 'High',
      critical: 'Critical',
    };
    return locale === 'ar' ? ar[severity] || severity : en[severity] || severity;
  },
  getHealthScoreColor: (score: number) => {
    if (score >= 80) return 'text-green-700 bg-green-100';
    if (score >= 60) return 'text-green-600 bg-green-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  },
}));

// ─── AlertBadge ───────────────────────────────────────────────────────────────
import AlertBadge from '../AlertBadge';

describe('AlertBadge Component', () => {
  it('renders low severity badge in Arabic', () => {
    render(<AlertBadge severity="low" />);
    expect(screen.getByText('منخفض')).toBeInTheDocument();
  });

  it('renders medium severity badge in Arabic', () => {
    render(<AlertBadge severity="medium" />);
    expect(screen.getByText('متوسط')).toBeInTheDocument();
  });

  it('renders high severity badge in Arabic', () => {
    render(<AlertBadge severity="high" />);
    expect(screen.getByText('مرتفع')).toBeInTheDocument();
  });

  it('renders critical severity badge in Arabic', () => {
    render(<AlertBadge severity="critical" />);
    expect(screen.getByText('حرج')).toBeInTheDocument();
  });

  it("renders in English when locale is 'en'", () => {
    render(<AlertBadge severity="critical" locale="en" />);
    expect(screen.getByText('Critical')).toBeInTheDocument();
  });

  it('renders as span element', () => {
    render(<AlertBadge severity="low" />);
    const badge = screen.getByText('منخفض');
    expect(badge.tagName).toBe('SPAN');
  });

  it('applies custom className', () => {
    render(<AlertBadge severity="high" className="custom-badge" />);
    expect(screen.getByText('مرتفع').className).toMatch(/custom-badge/);
  });

  it('applies rounded-full class for pill shape', () => {
    render(<AlertBadge severity="medium" />);
    expect(screen.getByText('متوسط').className).toMatch(/rounded-full/);
  });

  it('applies green styling for low severity', () => {
    render(<AlertBadge severity="low" />);
    expect(screen.getByText('منخفض').className).toMatch(/text-green-600/);
  });

  it('applies red styling for critical severity', () => {
    render(<AlertBadge severity="critical" />);
    expect(screen.getByText('حرج').className).toMatch(/text-red-600/);
  });
});

// ─── StatusBadge ──────────────────────────────────────────────────────────────
import StatusBadge from '../StatusBadge';

describe('StatusBadge Component', () => {
  it('renders active status in Arabic', () => {
    render(<StatusBadge status="active" />);
    expect(screen.getByText('نشط')).toBeInTheDocument();
  });

  it('renders inactive status in Arabic', () => {
    render(<StatusBadge status="inactive" />);
    expect(screen.getByText('غير نشط')).toBeInTheDocument();
  });

  it('renders pending status in Arabic', () => {
    render(<StatusBadge status="pending" />);
    expect(screen.getByText('قيد الانتظار')).toBeInTheDocument();
  });

  it('renders confirmed status in Arabic', () => {
    render(<StatusBadge status="confirmed" />);
    expect(screen.getByText('مؤكد')).toBeInTheDocument();
  });

  it("renders in English when locale is 'en'", () => {
    render(<StatusBadge status="active" locale="en" />);
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('applies correct color for active status', () => {
    render(<StatusBadge status="active" />);
    expect(screen.getByText('نشط').className).toMatch(/text-green-600/);
  });

  it('applies correct color for inactive status', () => {
    render(<StatusBadge status="inactive" />);
    expect(screen.getByText('غير نشط').className).toMatch(/text-red-600/);
  });

  it('applies correct color for pending status', () => {
    render(<StatusBadge status="pending" />);
    expect(screen.getByText('قيد الانتظار').className).toMatch(/text-yellow-600/);
  });

  it('renders as span element with rounded-full class', () => {
    render(<StatusBadge status="active" />);
    const badge = screen.getByText('نشط');
    expect(badge.tagName).toBe('SPAN');
    expect(badge.className).toMatch(/rounded-full/);
  });

  it('applies custom className', () => {
    render(<StatusBadge status="active" className="my-custom" />);
    expect(screen.getByText('نشط').className).toMatch(/my-custom/);
  });
});

// ─── StatCard ─────────────────────────────────────────────────────────────────
import StatCard from '../StatCard';

// Simple icon component for StatCard tests
const MockIcon = (props: Record<string, unknown>) =>
  React.createElement('svg', { 'data-testid': 'icon-MockIcon', ...props });

describe('StatCard Component', () => {
  it('renders title text', () => {
    render(<StatCard title="إجمالي الحقول" value={42} icon={MockIcon} />);
    expect(screen.getByText('إجمالي الحقول')).toBeInTheDocument();
  });

  it('renders numeric value', () => {
    render(<StatCard title="عدد المزارعين" value={150} icon={MockIcon} />);
    expect(screen.getByText('150')).toBeInTheDocument();
  });

  it('renders string value', () => {
    render(<StatCard title="الحالة" value="نشط" icon={MockIcon} />);
    expect(screen.getByText('نشط')).toBeInTheDocument();
  });

  it('renders suffix when provided', () => {
    render(<StatCard title="المساحة" value={100} icon={MockIcon} suffix="هكتار" />);
    expect(screen.getByText('هكتار')).toBeInTheDocument();
  });

  it('renders positive trend indicator', () => {
    render(
      <StatCard title="النمو" value={200} icon={MockIcon} trend={{ value: 12, isPositive: true }} />
    );
    expect(screen.getByText('↑')).toBeInTheDocument();
    expect(screen.getByText('12%')).toBeInTheDocument();
    expect(screen.getByText('من الأسبوع الماضي')).toBeInTheDocument();
  });

  it('renders negative trend indicator', () => {
    render(
      <StatCard
        title="التراجع"
        value={80}
        icon={MockIcon}
        trend={{ value: 5, isPositive: false }}
      />
    );
    expect(screen.getByText('↓')).toBeInTheDocument();
    expect(screen.getByText('5%')).toBeInTheDocument();
  });

  it('applies green color for positive trend', () => {
    render(
      <StatCard title="Test" value={10} icon={MockIcon} trend={{ value: 10, isPositive: true }} />
    );
    const trendContainer = screen.getByText('↑').closest('p');
    expect(trendContainer?.className).toMatch(/text-green-600/);
  });

  it('applies red color for negative trend', () => {
    render(
      <StatCard title="Test" value={10} icon={MockIcon} trend={{ value: 5, isPositive: false }} />
    );
    const trendContainer = screen.getByText('↓').closest('p');
    expect(trendContainer?.className).toMatch(/text-red-600/);
  });

  it('renders icon', () => {
    render(<StatCard title="Test" value={10} icon={MockIcon} />);
    expect(screen.getByTestId('icon-MockIcon')).toBeInTheDocument();
  });

  it('renders without trend when not provided', () => {
    render(<StatCard title="Test" value={10} icon={MockIcon} />);
    expect(screen.queryByText('من الأسبوع الماضي')).not.toBeInTheDocument();
  });

  it('renders without suffix when not provided', () => {
    render(<StatCard title="Test" value={10} icon={MockIcon} />);
    // Should not have any suffix element
    const valueEl = screen.getByText('10');
    expect(valueEl).toBeInTheDocument();
  });
});

// ─── DataTable ────────────────────────────────────────────────────────────────
import DataTable from '../DataTable';

interface TestRow {
  id: string;
  name: string;
  status: string;
}

const testColumns = [
  { key: 'name', header: 'الاسم' },
  {
    key: 'status',
    header: 'الحالة',
    render: (item: TestRow) => <span data-testid="status-cell">{item.status}</span>,
  },
];

const testData: TestRow[] = [
  { id: '1', name: 'أحمد محمد', status: 'نشط' },
  { id: '2', name: 'فاطمة علي', status: 'غير نشط' },
  { id: '3', name: 'خالد عبدالله', status: 'قيد الانتظار' },
];

describe('DataTable Component', () => {
  it('renders column headers', () => {
    render(<DataTable columns={testColumns} data={testData} keyExtractor={(item) => item.id} />);
    expect(screen.getByText('الاسم')).toBeInTheDocument();
    expect(screen.getByText('الحالة')).toBeInTheDocument();
  });

  it('renders all rows', () => {
    render(<DataTable columns={testColumns} data={testData} keyExtractor={(item) => item.id} />);
    expect(screen.getByText('أحمد محمد')).toBeInTheDocument();
    expect(screen.getByText('فاطمة علي')).toBeInTheDocument();
    expect(screen.getByText('خالد عبدالله')).toBeInTheDocument();
  });

  it('renders custom cell content via render function', () => {
    render(<DataTable columns={testColumns} data={testData} keyExtractor={(item) => item.id} />);
    const statusCells = screen.getAllByTestId('status-cell');
    expect(statusCells).toHaveLength(3);
  });

  it('shows empty message when data is empty', () => {
    render(
      <DataTable
        columns={testColumns}
        data={[]}
        keyExtractor={(item) => (item as TestRow).id}
        emptyMessage="لا توجد بيانات متاحة"
      />
    );
    expect(screen.getByText('لا توجد بيانات متاحة')).toBeInTheDocument();
  });

  it('shows default empty message when no data and no custom message', () => {
    render(
      <DataTable columns={testColumns} data={[]} keyExtractor={(item) => (item as TestRow).id} />
    );
    expect(screen.getByText('لا توجد بيانات')).toBeInTheDocument();
  });

  it('shows loading skeleton when isLoading is true', () => {
    const { container } = render(
      <DataTable
        columns={testColumns}
        data={[]}
        keyExtractor={(item) => (item as TestRow).id}
        isLoading={true}
      />
    );
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('calls onRowClick when row is clicked', () => {
    const onRowClick = vi.fn();
    render(
      <DataTable
        columns={testColumns}
        data={testData}
        keyExtractor={(item) => item.id}
        onRowClick={onRowClick}
      />
    );
    fireEvent.click(screen.getByText('أحمد محمد'));
    expect(onRowClick).toHaveBeenCalledWith(testData[0]);
  });

  it('calls onRowClick on Enter keydown', () => {
    const onRowClick = vi.fn();
    render(
      <DataTable
        columns={testColumns}
        data={testData}
        keyExtractor={(item) => item.id}
        onRowClick={onRowClick}
      />
    );
    const row = screen.getByText('أحمد محمد').closest('tr');
    if (row) {
      fireEvent.keyDown(row, { key: 'Enter' });
      expect(onRowClick).toHaveBeenCalledWith(testData[0]);
    }
  });

  it('renders a table element', () => {
    const { container } = render(
      <DataTable columns={testColumns} data={testData} keyExtractor={(item) => item.id} />
    );
    expect(container.querySelector('table')).toBeInTheDocument();
  });

  it('applies custom className to wrapper', () => {
    const { container } = render(
      <DataTable
        columns={testColumns}
        data={testData}
        keyExtractor={(item) => item.id}
        className="custom-table"
      />
    );
    expect(container.querySelector('.custom-table')).toBeInTheDocument();
  });
});

// ─── SearchFilter ─────────────────────────────────────────────────────────────
import SearchFilter from '../SearchFilter';

describe('SearchFilter Component', () => {
  it('renders search input with default Arabic placeholder', () => {
    render(<SearchFilter />);
    expect(screen.getByPlaceholderText('بحث...')).toBeInTheDocument();
  });

  it('displays current search value when controlled', () => {
    render(<SearchFilter searchValue="قمح" onSearchChange={vi.fn()} />);
    const input = screen.getByPlaceholderText('بحث...');
    expect(input).toHaveValue('قمح');
  });

  it('calls onSearchChange when user types', () => {
    const onSearchChange = vi.fn();
    render(<SearchFilter onSearchChange={onSearchChange} />);
    const input = screen.getByPlaceholderText('بحث...');
    fireEvent.change(input, { target: { value: 'ذرة' } });
    // Value should update in uncontrolled state
    expect(input).toHaveValue('ذرة');
  });

  it('renders with custom Arabic placeholder', () => {
    render(<SearchFilter searchPlaceholderAr="ابحث عن حقل..." />);
    expect(screen.getByPlaceholderText('ابحث عن حقل...')).toBeInTheDocument();
  });

  it('shows search icon', () => {
    render(<SearchFilter />);
    expect(screen.getByTestId('icon-Search')).toBeInTheDocument();
  });

  it('has aria-label matching placeholder', () => {
    render(<SearchFilter searchPlaceholderAr="ابحث..." />);
    expect(screen.getByLabelText('ابحث...')).toBeInTheDocument();
  });
});

// ─── Breadcrumbs ──────────────────────────────────────────────────────────────
import Breadcrumbs from '../Breadcrumbs';

describe('Breadcrumbs Component', () => {
  it('renders nav element with aria-label', () => {
    render(<Breadcrumbs items={[{ label: 'الحقول', href: '/admin/fields' }]} />);
    expect(screen.getByRole('navigation')).toHaveAttribute('aria-label', 'مسار التنقل');
  });

  it('renders provided breadcrumb items', () => {
    render(
      <Breadcrumbs
        items={[
          { label: 'لوحة التحكم', href: '/admin' },
          { label: 'المزارعون', href: '/admin/users' },
          { label: 'أحمد محمد' },
        ]}
      />
    );
    expect(screen.getByText('لوحة التحكم')).toBeInTheDocument();
    expect(screen.getByText('المزارعون')).toBeInTheDocument();
    expect(screen.getByText('أحمد محمد')).toBeInTheDocument();
  });

  it('renders links for items with href (non-last items are links)', () => {
    render(
      <Breadcrumbs
        items={[{ label: 'لوحة التحكم', href: '/admin' }, { label: 'الصفحة الحالية' }]}
      />
    );
    // "لوحة التحكم" is not the last item so it renders as a link
    const link = screen.getByText('لوحة التحكم').closest('a');
    expect(link).toBeTruthy();
    // "الصفحة الحالية" is the last item (current page), not a link
    const currentPage = screen.getByText('الصفحة الحالية');
    expect(currentPage.tagName).not.toBe('A');
  });

  it('shows home breadcrumb by default', () => {
    render(<Breadcrumbs items={[{ label: 'الحقول', href: '/admin/fields' }]} />);
    // Home link should show Home icon
    expect(screen.getByTestId('icon-Home')).toBeInTheDocument();
    expect(screen.getByText('الرئيسية')).toBeInTheDocument();
  });

  it('does not render home when showHome is false', () => {
    render(<Breadcrumbs items={[{ label: 'الحقول' }]} showHome={false} />);
    expect(screen.queryByTestId('icon-Home')).not.toBeInTheDocument();
  });

  it('applies custom className to nav', () => {
    const { container } = render(
      <Breadcrumbs items={[{ label: 'الحقول' }]} className="custom-breadcrumb" />
    );
    expect(container.querySelector('.custom-breadcrumb')).toBeInTheDocument();
  });
});

// ─── Admin ErrorBoundary ──────────────────────────────────────────────────────
import { ErrorBoundary } from '../../common/ErrorBoundary';

const ThrowingComponent = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) throw new Error('Test error in admin');
  return <div>Admin content is fine</div>;
};

const originalConsoleError = console.error;

describe('Admin ErrorBoundary', () => {
  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={false} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Admin content is fine')).toBeInTheDocument();
  });

  it('shows admin error UI when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('خطأ في لوحة التحكم')).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Test error in admin')).toBeInTheDocument();
  });

  it('shows retry button', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('إعادة المحاولة')).toBeInTheDocument();
  });

  it('shows page refresh button', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('تحديث الصفحة')).toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();
    render(
      <ErrorBoundary onError={onError}>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(onError).toHaveBeenCalled();
  });

  it('uses fallback when provided', () => {
    render(
      <ErrorBoundary fallback={<div>Custom fallback</div>}>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Custom fallback')).toBeInTheDocument();
  });

  it('resets error state when retry button is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary key="err">
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('خطأ في لوحة التحكم')).toBeInTheDocument();

    // Re-render with new key without error
    rerender(
      <ErrorBoundary key="ok">
        <ThrowingComponent shouldThrow={false} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Admin content is fine')).toBeInTheDocument();
  });
});
