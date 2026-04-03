/**
 * Field Detail Page Tests
 * اختبارات صفحة تفاصيل الحقل
 *
 * Tests the field detail page (/farms/[id]/page.tsx):
 * - Loading state rendering
 * - Field info display (name, crop type, area, status)
 * - Map component rendering
 * - Weather data display
 * - NDVI/health status panel
 * - Error state handling
 * - Agricultural KPI display
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

// Mock next/navigation
const mockPush = vi.fn();
const mockBack = vi.fn();
vi.mock('next/navigation', () => ({
  useParams: () => ({ id: 'test-field-id' }),
  useRouter: () => ({ push: mockPush, back: mockBack }),
}));

// Mock next/dynamic for map component
vi.mock('next/dynamic', () => ({
  __esModule: true,
  default: () => {
    const _React = require('react');
    return function MockFarmsMap(props: any) {
      return _React.createElement('div', {
        'data-testid': 'farms-map',
        'data-farms-count': props.farms?.length ?? 0,
      });
    };
  },
}));

// Mock useField hook
const mockUseField = vi.fn();
vi.mock('@/hooks/api/use-fields', () => ({
  useField: (...args: unknown[]) => mockUseField(...args),
}));

// Mock weather hooks
const mockUseWeatherCurrent = vi.fn();
const mockUseWeatherForecast = vi.fn();
const mockUseAgriculturalReport = vi.fn();
vi.mock('@/hooks/api/use-weather', () => ({
  useWeatherCurrent: (...args: unknown[]) => mockUseWeatherCurrent(...args),
  useWeatherForecast: (...args: unknown[]) => mockUseWeatherForecast(...args),
  useAgriculturalReport: (...args: unknown[]) => mockUseAgriculturalReport(...args),
}));

// Mock apiClient (still needed for other imports)
const mockApiGet = vi.fn();
vi.mock('@/lib/api', () => ({
  apiClient: {
    get: (...args: unknown[]) => mockApiGet(...args),
  },
}));

// Mock global fetch for NDVI satellite proxy calls (/api/satellite?...)
const mockFetchFn = vi.fn();
globalThis.fetch = mockFetchFn as unknown as typeof fetch;

// Helper: set both apiClient and fetch mocks for NDVI data
function setNdviMockData(data: Record<string, unknown>) {
  mockApiGet.mockResolvedValue({ data });
  mockFetchFn.mockResolvedValue({ ok: true, json: async () => data });
}
function setNdviMockError() {
  mockApiGet.mockRejectedValue(new Error('Failed'));
  mockFetchFn.mockRejectedValue(new Error('Failed'));
}

// Mock @/components/maps/FarmsMap type import
vi.mock('@/components/maps/FarmsMap', () => ({
  __esModule: true,
  default: () => null,
}));

// Mock @/lib/utils
vi.mock('@/lib/utils', () => ({
  cn: (...inputs: string[]) => inputs.filter(Boolean).join(' '),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => {
  const _React = require('react');
  const createIcon = (name: string) => {
    const Icon = (props: Record<string, unknown>) =>
      _React.createElement('svg', { 'data-testid': `icon-${name}`, ...props });
    Icon.displayName = name;
    return Icon;
  };
  return {
    __esModule: true,
    MapPin: createIcon('MapPin'),
    Leaf: createIcon('Leaf'),
    Droplets: createIcon('Droplets'),
    Wind: createIcon('Wind'),
    Thermometer: createIcon('Thermometer'),
    CloudRain: createIcon('CloudRain'),
    Sun: createIcon('Sun'),
    TrendingUp: createIcon('TrendingUp'),
    TrendingDown: createIcon('TrendingDown'),
    Minus: createIcon('Minus'),
    AlertTriangle: createIcon('AlertTriangle'),
    RefreshCw: createIcon('RefreshCw'),
    Calendar: createIcon('Calendar'),
    Sprout: createIcon('Sprout'),
    Activity: createIcon('Activity'),
  };
});

import FieldDetailPage from '../../farms/[id]/page';

// ═══════════════════════════════════════════════════════════════════════════
// Test Data
// ═══════════════════════════════════════════════════════════════════════════

const sampleField = {
  id: 'test-field-id',
  name: 'North Wheat Field',
  nameAr: 'حقل القمح الشمالي',
  coordinates: { lat: 15.55, lng: 48.51 },
  area: 12.5,
  crops: ['قمح'],
  status: 'active',
  healthScore: 82,
  createdAt: '2025-06-15T10:00:00Z',
  lastUpdated: '2026-03-20T14:30:00Z',
};

const sampleWeather = {
  temperature_c: 28,
  humidity_percent: 45,
  wind_speed_kmh: 12,
  precipitation_mm: 0,
  condition: 'صافي',
};

const sampleForecast = {
  daily: [
    { date: '2026-04-03', temp_max_c: 30, temp_min_c: 18 },
    { date: '2026-04-04', temp_max_c: 32, temp_min_c: 20 },
    { date: '2026-04-05', temp_max_c: 29, temp_min_c: 17 },
  ],
};

const sampleAgReport = {
  et0: 5.2,
  gdd: 180,
  spray_window: true,
};

// Default hook return for loaded state (no data)
const defaultHookReturn = {
  data: null,
  isLoading: false,
  isError: false,
  refetch: vi.fn(),
};

// ═══════════════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('FieldDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default: NDVI fetch via global fetch (satellite proxy)
    mockFetchFn.mockResolvedValue({
      ok: true,
      json: async () => ({ ndvi: 0.72, lai: 3.1, health_status: 'healthy', trend: 'up' }),
    });
    // Keep apiClient mock for any other uses
    setNdviMockData({ ndvi: 0.72, lai: 3.1, health_status: 'healthy', trend: 'up' });

    // Default hook states
    mockUseWeatherCurrent.mockReturnValue({ ...defaultHookReturn });
    mockUseWeatherForecast.mockReturnValue({ ...defaultHookReturn });
    mockUseAgriculturalReport.mockReturnValue({ ...defaultHookReturn });
  });

  // ─── Loading State ──────────────────────────────────────────────────────

  describe('loading state', () => {
    it('renders loading skeleton when field is loading', () => {
      mockUseField.mockReturnValue({
        data: null,
        isLoading: true,
        isError: false,
        refetch: vi.fn(),
      });

      const { container } = render(<FieldDetailPage />);
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('does not render field name during loading', () => {
      mockUseField.mockReturnValue({
        data: null,
        isLoading: true,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.queryByText('حقل القمح الشمالي')).not.toBeInTheDocument();
    });
  });

  // ─── Field Info Display ─────────────────────────────────────────────────

  describe('field info display', () => {
    beforeEach(() => {
      mockUseField.mockReturnValue({
        data: sampleField,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });
    });

    it('displays field Arabic name', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText('حقل القمح الشمالي')).toBeInTheDocument();
    });

    it('displays field English name as subtitle', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText('North Wheat Field')).toBeInTheDocument();
    });

    it('displays crop type', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText('قمح')).toBeInTheDocument();
    });

    it('displays field area in hectares', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText(/12\.5/)).toBeInTheDocument();
      expect(screen.getByText(/هكتار/)).toBeInTheDocument();
    });

    it('displays field status badge', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText('نشط')).toBeInTheDocument();
    });

    it('displays health score percentage', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText('82%')).toBeInTheDocument();
    });

    it('renders page with RTL direction', () => {
      const { container } = render(<FieldDetailPage />);
      const rtlElement = container.querySelector('[dir="rtl"]');
      expect(rtlElement).toBeInTheDocument();
    });

    it('displays creation date', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText(/تاريخ الإنشاء/)).toBeInTheDocument();
    });

    it('displays last updated date', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText(/آخر تحديث/)).toBeInTheDocument();
    });
  });

  // ─── Map Component ─────────────────────────────────────────────────────

  describe('map component', () => {
    it('renders map when field has coordinates', () => {
      mockUseField.mockReturnValue({
        data: sampleField,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByTestId('farms-map')).toBeInTheDocument();
    });

    it('shows map section header "موقع الحقل"', () => {
      mockUseField.mockReturnValue({
        data: sampleField,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('موقع الحقل')).toBeInTheDocument();
    });

    it('shows message when no coordinates available', () => {
      mockUseField.mockReturnValue({
        data: { ...sampleField, coordinates: null },
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('لا توجد إحداثيات متاحة')).toBeInTheDocument();
    });
  });

  // ─── Weather Panel ──────────────────────────────────────────────────────

  describe('weather panel', () => {
    beforeEach(() => {
      mockUseField.mockReturnValue({
        data: sampleField,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });
    });

    it('shows weather section header "الطقس الحالي"', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText('الطقس الحالي')).toBeInTheDocument();
    });

    it('displays temperature when weather data is loaded', () => {
      mockUseWeatherCurrent.mockReturnValue({
        data: sampleWeather,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      // Temperature rendered as "28°"
      expect(screen.getByText(/28/)).toBeInTheDocument();
    });

    it('displays humidity percentage', () => {
      mockUseWeatherCurrent.mockReturnValue({
        data: sampleWeather,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('45%')).toBeInTheDocument();
    });

    it('shows humidity label "الرطوبة"', () => {
      mockUseWeatherCurrent.mockReturnValue({
        data: sampleWeather,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('الرطوبة')).toBeInTheDocument();
    });

    it('shows wind label "الرياح"', () => {
      mockUseWeatherCurrent.mockReturnValue({
        data: sampleWeather,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('الرياح')).toBeInTheDocument();
    });

    it('shows rain label "المطر"', () => {
      mockUseWeatherCurrent.mockReturnValue({
        data: sampleWeather,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('المطر')).toBeInTheDocument();
    });

    it('shows weather error card when weather fetch fails', () => {
      mockUseWeatherCurrent.mockReturnValue({
        data: null,
        isLoading: false,
        isError: true,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('تعذر تحميل بيانات الطقس')).toBeInTheDocument();
    });

    it('shows weather loading skeleton when loading', () => {
      mockUseWeatherCurrent.mockReturnValue({
        data: null,
        isLoading: true,
        isError: false,
        refetch: vi.fn(),
      });

      const { container } = render(<FieldDetailPage />);
      // There should be skeleton elements
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  // ─── NDVI/Health Panel ──────────────────────────────────────────────────

  describe('NDVI panel', () => {
    beforeEach(() => {
      mockUseField.mockReturnValue({
        data: sampleField,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });
    });

    it('shows NDVI section header', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText(/صحة الغطاء النباتي/)).toBeInTheDocument();
      expect(screen.getByText(/NDVI/)).toBeInTheDocument();
    });

    it('displays health status label "صحي" for healthy status', async () => {
      setNdviMockData({
        ndvi: 0.72, lai: 3.1, health_status: 'healthy', trend: 'up' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('صحي')).toBeInTheDocument();
      });
    });

    it('displays NDVI value', async () => {
      setNdviMockData({
        ndvi: 0.72, lai: 3.1, health_status: 'healthy' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('0.72')).toBeInTheDocument();
      });
    });

    it('displays LAI value', async () => {
      setNdviMockData({
        ndvi: 0.72, lai: 3.1, health_status: 'healthy' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('3.1')).toBeInTheDocument();
      });
    });

    it('shows LAI label in Arabic', async () => {
      setNdviMockData({
        ndvi: 0.72, lai: 3.1, health_status: 'healthy' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText(/مؤشر مساحة الورقة/)).toBeInTheDocument();
      });
    });

    it('shows NDVI value label in Arabic', async () => {
      setNdviMockData({
        ndvi: 0.72, lai: 3.1, health_status: 'healthy' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('قيمة NDVI')).toBeInTheDocument();
      });
    });

    it('shows error card when NDVI fetch fails', async () => {
      setNdviMockError();

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('تعذر تحميل بيانات القمر الصناعي')).toBeInTheDocument();
      });
    });

    it('displays "معتدل" for moderate health status', async () => {
      setNdviMockData({
        ndvi: 0.45, lai: 2.0, health_status: 'moderate' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('معتدل')).toBeInTheDocument();
      });
    });

    it('displays "مجهد" for stressed health status', async () => {
      setNdviMockData({
        ndvi: 0.25, lai: 1.0, health_status: 'stressed' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('مجهد')).toBeInTheDocument();
      });
    });

    it('displays "حرج" for critical health status', async () => {
      setNdviMockData({
        ndvi: 0.12, lai: 0.5, health_status: 'critical' });

      render(<FieldDetailPage />);

      await waitFor(() => {
        expect(screen.getByText('حرج')).toBeInTheDocument();
      });
    });
  });

  // ─── Error State ────────────────────────────────────────────────────────

  describe('error state', () => {
    it('renders error card when field fetch fails', () => {
      mockUseField.mockReturnValue({
        data: null,
        isLoading: false,
        isError: true,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(
        screen.getByText('تعذر تحميل بيانات الحقل. يرجى المحاولة مرة أخرى.')
      ).toBeInTheDocument();
    });

    it('renders retry button on field error', () => {
      mockUseField.mockReturnValue({
        data: null,
        isLoading: false,
        isError: true,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('إعادة المحاولة')).toBeInTheDocument();
    });

    it('does not render field info on error', () => {
      mockUseField.mockReturnValue({
        data: null,
        isLoading: false,
        isError: true,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.queryByText('حقل القمح الشمالي')).not.toBeInTheDocument();
      expect(screen.queryByText('موقع الحقل')).not.toBeInTheDocument();
    });
  });

  // ─── Forecast & Agricultural KPIs ───────────────────────────────────────

  describe('forecast and agricultural KPIs', () => {
    beforeEach(() => {
      mockUseField.mockReturnValue({
        data: sampleField,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });
    });

    it('shows forecast section header', () => {
      render(<FieldDetailPage />);
      expect(screen.getByText('التوقعات والمؤشرات الزراعية')).toBeInTheDocument();
    });

    it('shows forecast label "التوقعات - 7 أيام"', () => {
      mockUseWeatherForecast.mockReturnValue({
        data: sampleForecast,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('التوقعات - 7 أيام')).toBeInTheDocument();
    });

    it('shows forecast error card when fetch fails', () => {
      mockUseWeatherForecast.mockReturnValue({
        data: null,
        isLoading: false,
        isError: true,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('تعذر تحميل التوقعات')).toBeInTheDocument();
    });

    it('shows agricultural KPIs when report is available', () => {
      mockUseAgriculturalReport.mockReturnValue({
        data: sampleAgReport,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('المؤشرات الزراعية')).toBeInTheDocument();
    });

    it('displays ET0 value from agricultural report', () => {
      mockUseAgriculturalReport.mockReturnValue({
        data: sampleAgReport,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText(/التبخر-نتح/)).toBeInTheDocument();
      expect(screen.getByText(/5\.2/)).toBeInTheDocument();
    });

    it('displays GDD value from agricultural report', () => {
      mockUseAgriculturalReport.mockReturnValue({
        data: sampleAgReport,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText(/وحدات حرارة النمو/)).toBeInTheDocument();
      expect(screen.getByText('180')).toBeInTheDocument();
    });

    it('displays spray window status "مناسبة" when true', () => {
      mockUseAgriculturalReport.mockReturnValue({
        data: sampleAgReport,
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText(/نافذة الرش/)).toBeInTheDocument();
      expect(screen.getByText('مناسبة')).toBeInTheDocument();
    });

    it('displays spray window status "غير مناسبة" when false', () => {
      mockUseAgriculturalReport.mockReturnValue({
        data: { ...sampleAgReport, spray_window: false },
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('غير مناسبة')).toBeInTheDocument();
    });

    it('shows agricultural report error when fetch fails', () => {
      mockUseAgriculturalReport.mockReturnValue({
        data: null,
        isLoading: false,
        isError: true,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('تعذر تحميل التقرير الزراعي')).toBeInTheDocument();
    });
  });

  // ─── Status Badge Variants ──────────────────────────────────────────────

  describe('status badges', () => {
    it('shows "بور" for fallow status', () => {
      mockUseField.mockReturnValue({
        data: { ...sampleField, status: 'fallow' },
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('بور')).toBeInTheDocument();
    });

    it('shows "تم الحصاد" for harvested status', () => {
      mockUseField.mockReturnValue({
        data: { ...sampleField, status: 'harvested' },
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('تم الحصاد')).toBeInTheDocument();
    });

    it('shows "مخطط" for planned status', () => {
      mockUseField.mockReturnValue({
        data: { ...sampleField, status: 'planned' },
        isLoading: false,
        isError: false,
        refetch: vi.fn(),
      });

      render(<FieldDetailPage />);
      expect(screen.getByText('مخطط')).toBeInTheDocument();
    });
  });

  // ─── Source Verification ────────────────────────────────────────────────

  describe('source verification', () => {
    const fs = require('fs');
    const path = require('path');
    const filePath = path.resolve(__dirname, '../../farms/[id]/page.tsx');

    it('field detail page source file exists', () => {
      expect(fs.existsSync(filePath)).toBe(true);
    });

    it('exports a default component', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('export default function FieldDetailPage');
    });

    it('uses useField hook for data fetching', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('useField');
    });

    it('uses weather hooks', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('useWeatherCurrent');
      expect(content).toContain('useWeatherForecast');
      expect(content).toContain('useAgriculturalReport');
    });

    it('has NDVI health classification function', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('getHealthColor');
      expect(content).toContain('getHealthLabel');
    });

    it('supports all health statuses in Arabic', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('صحي');
      expect(content).toContain('معتدل');
      expect(content).toContain('مجهد');
      expect(content).toContain('حرج');
    });

    it('uses dynamic import for FarmsMap', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('dynamic');
      expect(content).toContain('FarmsMap');
      expect(content).toContain('ssr: false');
    });

    it('has ErrorCard component for error handling', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('ErrorCard');
      expect(content).toContain('إعادة المحاولة');
    });

    it('has skeleton loading components', () => {
      const content = fs.readFileSync(filePath, 'utf-8');
      expect(content).toContain('CardSkeleton');
      expect(content).toContain('animate-pulse');
    });
  });
});
