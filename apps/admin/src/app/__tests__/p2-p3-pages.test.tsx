/**
 * P2/P3 Feature Pages Tests
 * اختبارات صفحات ميزات P2/P3
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

// ═══════════════════════════════════════════════════════════════════════════
// Global Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock('next/navigation', () => ({
  usePathname: () => '/analytics/yield-forecasting',
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

vi.mock('next/dynamic', () => ({
  default: (_loader: () => Promise<{ default: React.ComponentType }>, _opts?: unknown) => {
    const DynamicComponent = (props: Record<string, unknown>) =>
      React.createElement('div', { 'data-testid': 'dynamic-component', ...props });
    DynamicComponent.displayName = 'DynamicComponent';
    return DynamicComponent;
  },
}));

vi.mock('@/lib/logger', () => ({
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

vi.mock('@/stores/auth.store', () => ({
  useAuth: () => ({
    user: { id: '1', email: 'admin@sahool.io', name: 'Admin', name_ar: 'مدير', role: 'admin' },
    isAuthenticated: true,
    isLoading: false,
    logout: vi.fn(),
    login: vi.fn(),
    checkAuth: vi.fn(),
  }),
}));

vi.mock('@/stores/theme.store', () => ({
  useTheme: () => ({
    theme: 'light',
    resolvedTheme: 'light',
    setTheme: vi.fn(),
    toggleTheme: vi.fn(),
  }),
}));

vi.mock('@/lib/utils', () => ({
  cn: (...inputs: (string | undefined | null | false)[]) => inputs.filter(Boolean).join(' '),
}));

vi.mock('@/components/layout/Header', () => ({
  default: ({ title, subtitle }: { title: string; subtitle?: string }) =>
    React.createElement(
      'header',
      { 'data-testid': 'header' },
      React.createElement('h1', { 'data-testid': 'header-title' }, title),
      subtitle && React.createElement('p', { 'data-testid': 'header-subtitle' }, subtitle)
    ),
}));

vi.mock('@/components/ui/StatCard', () => ({
  default: ({ title, value }: { title: string; value: string | number; [key: string]: unknown }) =>
    React.createElement(
      'div',
      { 'data-testid': 'stat-card' },
      React.createElement('span', { 'data-testid': 'stat-title' }, title),
      React.createElement('span', { 'data-testid': 'stat-value' }, String(value))
    ),
}));

// Lucide-react mock — explicit exports with fallback for unknown icons
vi.mock('lucide-react', () => {
  const cache = new Map<string, React.FC<Record<string, unknown>>>();
  const createIcon = (name: string) => {
    if (cache.has(name)) return cache.get(name)!;
    const Icon = (props: Record<string, unknown>) =>
      React.createElement('svg', { 'data-testid': `icon-${name}`, ...props });
    Icon.displayName = name;
    cache.set(name, Icon);
    return Icon;
  };

  // Pre-built icons used across tested pages
  const icons: Record<string, React.FC<Record<string, unknown>>> = {};
  const names = [
    'TrendingUp',
    'BarChart3',
    'Leaf',
    'Calendar',
    'CheckCircle2',
    'ChevronDown',
    'Droplets',
    'Sun',
    'FlaskConical',
    'AlertTriangle',
    'Target',
    'Clock',
    'MapPin',
    'Activity',
    'Tractor',
    'Plane',
    'SprayCan',
    'Truck',
    'Wrench',
    'Gauge',
    'Fuel',
    'ChevronRight',
    'X',
    'RefreshCw',
    'Filter',
    'PauseCircle',
    'WifiOff',
    'Navigation',
    'Thermometer',
    'Battery',
    'Shield',
    'Users',
    'Layers',
    'Package',
    'DollarSign',
    'XCircle',
    'Wheat',
    'ShoppingCart',
    'Factory',
    'User',
    'BookOpen',
    'Box',
    'TrendingDown',
    'Minus',
    'BarChart2',
    'Bell',
    'ShoppingBasket',
    'Store',
    'Download',
    'Star',
    'ArrowUpRight',
    'ArrowDownRight',
    'Award',
    'FileText',
    'AlertCircle',
    'CloudRain',
    'Bug',
    'CloudSnow',
    'Waves',
    'CheckCircle',
    'Info',
    'Map',
    'TreePine',
    'Mountain',
    'Wind',
    'ChevronUp',
    'ArrowRight',
    'Search',
    'Coffee',
    'Cherry',
    'Apple',
    'ChevronLeft',
    'Globe',
    'Sprout',
  ];
  for (const name of names) {
    icons[name] = createIcon(name);
  }

  // Return object with __esModule and a getter fallback for any new icons
  return {
    __esModule: true,
    ...icons,
    // Fallback: if a page imports an icon not listed above, create it on demand
    get [Symbol.for('vitest:mock-fallback')]() {
      return createIcon;
    },
  };
});

// ═══════════════════════════════════════════════════════════════════════════
// 1. Yield Forecasting — تنبؤ الإنتاجية
// ═══════════════════════════════════════════════════════════════════════════

describe('Yield Forecasting Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with correct title', async () => {
    const Page = (await import('@/app/analytics/yield-forecasting/page')).default;
    render(React.createElement(Page));
    expect(screen.getByTestId('header-title')).toHaveTextContent('تنبؤ الإنتاجية');
  });

  it('renders 4 stat cards', async () => {
    const Page = (await import('@/app/analytics/yield-forecasting/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId('stat-card').length).toBe(4);
  });

  it('displays field prediction data', async () => {
    const Page = (await import('@/app/analytics/yield-forecasting/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/قمح/).length).toBeGreaterThan(0);
  });

  it('has filter tabs for crop types', async () => {
    const Page = (await import('@/app/analytics/yield-forecasting/page')).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 2. Fleet Tracking — تتبع الأسطول
// ═══════════════════════════════════════════════════════════════════════════

describe('Fleet Tracking Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with correct title', async () => {
    const Page = (await import('@/app/equipment/fleet-tracking/page')).default;
    render(React.createElement(Page));
    expect(screen.getByTestId('header-title')).toHaveTextContent('تتبع الأسطول');
  });

  it('renders stat cards', async () => {
    const Page = (await import('@/app/equipment/fleet-tracking/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId('stat-card').length).toBeGreaterThanOrEqual(1);
  });

  it('shows equipment mock data', async () => {
    const Page = (await import('@/app/equipment/fleet-tracking/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/جرار|طائرة|حصّادة|مرش|مضخة|شاحنة|رشاش/).length).toBeGreaterThan(0);
  });

  it('has filter controls', async () => {
    const Page = (await import('@/app/equipment/fleet-tracking/page')).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 3. Cooperatives — إدارة التعاونيات
// ═══════════════════════════════════════════════════════════════════════════

describe('Cooperatives Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with correct title', async () => {
    const Page = (await import('@/app/cooperatives/page')).default;
    render(React.createElement(Page));
    expect(screen.getByTestId('header-title')).toHaveTextContent('إدارة التعاونيات');
  });

  it('renders stat cards', async () => {
    const Page = (await import('@/app/cooperatives/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId('stat-card').length).toBeGreaterThanOrEqual(1);
  });

  it('shows cooperative data', async () => {
    const Page = (await import('@/app/cooperatives/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/تعاونية/).length).toBeGreaterThan(0);
  });

  it('has interactive elements', async () => {
    const Page = (await import('@/app/cooperatives/page')).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 4. Market Prices — أسعار السوق
// ═══════════════════════════════════════════════════════════════════════════

describe('Market Prices Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with correct title', async () => {
    const Page = (await import('@/app/market-prices/page')).default;
    render(React.createElement(Page));
    expect(screen.getByTestId('header-title')).toHaveTextContent('أسعار السوق');
  });

  it('renders stat cards', async () => {
    const Page = (await import('@/app/market-prices/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId('stat-card').length).toBeGreaterThanOrEqual(1);
  });

  it('shows crop price data', async () => {
    const Page = (await import('@/app/market-prices/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/قمح/).length).toBeGreaterThan(0);
  });

  it('has filter controls', async () => {
    const Page = (await import('@/app/market-prices/page')).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 5. Insurance — التأمين الزراعي
// ═══════════════════════════════════════════════════════════════════════════

describe('Insurance Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with correct title', async () => {
    const Page = (await import('@/app/insurance/page')).default;
    render(React.createElement(Page));
    expect(screen.getByTestId('header-title')).toHaveTextContent('التأمين الزراعي');
  });

  it('renders stat cards', async () => {
    const Page = (await import('@/app/insurance/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId('stat-card').length).toBeGreaterThanOrEqual(1);
  });

  it('shows policy data', async () => {
    const Page = (await import('@/app/insurance/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/POL-|أحمد|محمد|علي|خالد/).length).toBeGreaterThan(0);
  });

  it('has tab navigation', async () => {
    const Page = (await import('@/app/insurance/page')).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 6. Soil Map — خريطة التربة اليمنية
// ═══════════════════════════════════════════════════════════════════════════

describe('Soil Map Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with correct title', async () => {
    const Page = (await import('@/app/soil-map/page')).default;
    render(React.createElement(Page));
    expect(screen.getByTestId('header-title')).toHaveTextContent('خريطة التربة اليمنية');
  });

  it('renders stat cards', async () => {
    const Page = (await import('@/app/soil-map/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId('stat-card').length).toBeGreaterThanOrEqual(1);
  });

  it('shows agro-ecological zone data', async () => {
    const Page = (await import('@/app/soil-map/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText('تهامة').length).toBeGreaterThan(0);
  });

  it('shows highland zone', async () => {
    const Page = (await import('@/app/soil-map/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/المرتفعات/).length).toBeGreaterThan(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 7. Seeds Catalog — كتالوج البذور والأصناف
// ═══════════════════════════════════════════════════════════════════════════

describe('Seeds Catalog Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with correct title', async () => {
    const Page = (await import('@/app/seeds/page')).default;
    render(React.createElement(Page));
    expect(screen.getByTestId('header-title')).toHaveTextContent('كتالوج البذور والأصناف');
  });

  it('renders stat cards', async () => {
    const Page = (await import('@/app/seeds/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByTestId('stat-card').length).toBeGreaterThanOrEqual(1);
  });

  it('shows variety data', async () => {
    const Page = (await import('@/app/seeds/page')).default;
    render(React.createElement(Page));
    expect(screen.getAllByText(/قمح|بن|ذرة|نخيل|طماطم/).length).toBeGreaterThan(0);
  });

  it('has filter controls', async () => {
    const Page = (await import('@/app/seeds/page')).default;
    render(React.createElement(Page));
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
