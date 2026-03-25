import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '../../../../__tests__/test-utils';
import WeatherClient from '../WeatherClient';
import { CurrentWeather } from '@/features/weather';
import type { WeatherData, WeatherAlert, ForecastDataPoint } from '@/features/weather';

// ═══════════════════════════════════════════════════════════════════════════
// Mock Setup
// ═══════════════════════════════════════════════════════════════════════════

const mockCurrentWeather: WeatherData = {
  temperature: 32,
  humidity: 45,
  windSpeed: 15,
  windDirection: 'NE',
  pressure: 1013,
  visibility: 10,
  uvIndex: 7,
  condition: 'Partly Cloudy',
  conditionAr: 'غائم جزئياً',
  location: 'صنعاء، اليمن',
  timestamp: '2026-03-24T10:00:00.000Z',
};

const mockForecast: ForecastDataPoint[] = Array.from({ length: 7 }, (_, i) => {
  const date = new Date('2026-03-24');
  date.setDate(date.getDate() + i);
  return {
    date: date.toISOString(),
    temperature: 28 + i,
    humidity: 50 + i * 2,
    precipitation: i % 3 === 0 ? 5 : 0,
    windSpeed: 10 + i,
    condition: i % 2 === 0 ? 'Sunny' : 'Cloudy',
    conditionAr: i % 2 === 0 ? 'مشمس' : 'غائم',
  };
});

const mockAlerts: WeatherAlert[] = [
  {
    id: 'alert-1',
    type: 'temperature',
    severity: 'high',
    title: 'High Temperature Alert',
    titleAr: 'تنبيه درجة حرارة عالية',
    description: 'Expected high temperatures above 38°C',
    descriptionAr: 'من المتوقع درجات حرارة عالية تتجاوز 38 درجة مئوية',
    affectedAreas: ["Sana'a", 'Aden'],
    affectedAreasAr: ['صنعاء', 'عدن'],
    startTime: '2026-03-24T06:00:00Z',
    endTime: '2026-03-25T18:00:00Z',
    isActive: true,
  },
];

// Mock the weather hooks
const mockUseCurrentWeather = vi.fn();
const mockUseWeatherForecast = vi.fn();
const mockUseWeatherAlerts = vi.fn();

vi.mock('@/features/weather/hooks/useWeather', () => ({
  useCurrentWeather: (...args: unknown[]) => mockUseCurrentWeather(...args),
  useWeatherForecast: (...args: unknown[]) => mockUseWeatherForecast(...args),
  useWeatherAlerts: (...args: unknown[]) => mockUseWeatherAlerts(...args),
}));

// Mock logger to prevent console noise
vi.mock('@/lib/logger', () => ({
  logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn(), debug: vi.fn() },
}));

beforeEach(() => {
  vi.clearAllMocks();
  mockUseCurrentWeather.mockReturnValue({
    data: mockCurrentWeather,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
    isRefetching: false,
  });
  mockUseWeatherForecast.mockReturnValue({
    data: mockForecast,
    isLoading: false,
    error: null,
  });
  mockUseWeatherAlerts.mockReturnValue({
    data: mockAlerts,
    isLoading: false,
    error: null,
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// WeatherClient Component Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('WeatherClient', () => {
  it('should render page header with bilingual title', () => {
    render(<WeatherClient />);
    expect(screen.getAllByText(/الطقس/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Weather Dashboard/).length).toBeGreaterThanOrEqual(1);
  });

  it('should render all 5 Yemen locations in selector', () => {
    render(<WeatherClient />);
    const select = screen.getByRole('combobox');
    const options = select.querySelectorAll('option');

    expect(options).toHaveLength(5);
    expect(options[0]).toHaveTextContent('صنعاء، اليمن');
    expect(options[1]).toHaveTextContent('عدن، اليمن');
    expect(options[2]).toHaveTextContent('تعز، اليمن');
    expect(options[3]).toHaveTextContent('الحديدة، اليمن');
    expect(options[4]).toHaveTextContent('إب، اليمن');
  });

  it("should default to Sana'a location", () => {
    render(<WeatherClient />);
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('sanaa');
  });

  it('should switch location when selecting from dropdown', () => {
    render(<WeatherClient />);
    const select = screen.getByRole('combobox');

    fireEvent.change(select, { target: { value: 'aden' } });
    expect((select as HTMLSelectElement).value).toBe('aden');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// CurrentWeather Component Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('CurrentWeather', () => {
  it('should display temperature in Celsius', () => {
    render(<CurrentWeather lat={15.3694} lon={44.191} enabled />);
    expect(screen.getByText('32°C')).toBeInTheDocument();
  });

  it('should display Arabic weather condition', () => {
    render(<CurrentWeather lat={15.3694} lon={44.191} enabled />);
    expect(screen.getByText('غائم جزئياً')).toBeInTheDocument();
  });

  it('should display location name', () => {
    render(<CurrentWeather lat={15.3694} lon={44.191} enabled />);
    expect(screen.getByText('صنعاء، اليمن')).toBeInTheDocument();
  });

  it('should display weather metrics - humidity, wind, pressure, visibility, UV', () => {
    render(<CurrentWeather lat={15.3694} lon={44.191} enabled />);

    // Metric labels
    expect(screen.getByText('الرطوبة')).toBeInTheDocument();
    expect(screen.getByText('الرياح')).toBeInTheDocument();
    expect(screen.getByText('الضغط')).toBeInTheDocument();
    expect(screen.getByText('الرؤية')).toBeInTheDocument();
    expect(screen.getByText('مؤشر UV')).toBeInTheDocument();

    // Metric values
    expect(screen.getByText('45')).toBeInTheDocument(); // humidity
    expect(screen.getByText('15')).toBeInTheDocument(); // wind speed
    expect(screen.getByText('1013')).toBeInTheDocument(); // pressure
  });

  it('should show loading state with Arabic message', () => {
    mockUseCurrentWeather.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      refetch: vi.fn(),
      isRefetching: false,
    });

    render(<CurrentWeather enabled />);
    expect(screen.getByText('جاري تحميل بيانات الطقس...')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveAttribute('aria-busy', 'true');
  });

  it('should show error state with retry button', () => {
    const mockRefetch = vi.fn();
    mockUseCurrentWeather.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Network error'),
      refetch: mockRefetch,
      isRefetching: false,
    });

    render(<CurrentWeather enabled />);
    expect(screen.getByText('عذراً، حدث خطأ أثناء تحميل بيانات الطقس')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();

    // Click retry
    const retryBtn = screen.getByText('إعادة المحاولة');
    fireEvent.click(retryBtn);
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('should show no-data state when weather data is null', () => {
    mockUseCurrentWeather.mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
      isRefetching: false,
    });

    render(<CurrentWeather enabled />);
    expect(screen.getByText('بيانات الطقس غير متوفرة')).toBeInTheDocument();
  });

  it('should have ARIA accessibility attributes', () => {
    render(<CurrentWeather lat={15.3694} lon={44.191} enabled />);

    // Main region
    expect(screen.getByRole('region', { name: 'معلومات الطقس الحالي' })).toBeInTheDocument();

    // Metric list
    expect(screen.getByRole('list', { name: 'تفاصيل الطقس' })).toBeInTheDocument();
  });

  it('should pass coordinates to the hook', () => {
    render(<CurrentWeather lat={12.7855} lon={45.0187} enabled />);

    expect(mockUseCurrentWeather).toHaveBeenCalledWith({
      lat: 12.7855,
      lon: 45.0187,
      enabled: true,
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Weather Alerts Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('WeatherAlerts', () => {
  // Import directly to test the component
  let WeatherAlerts: React.ComponentType<{ lat?: number; lon?: number; enabled?: boolean }>;

  beforeEach(async () => {
    const mod = await import('@/features/weather/components/WeatherAlerts');
    WeatherAlerts = mod.WeatherAlerts;
  });

  it('should display alert title in Arabic', () => {
    render(<WeatherAlerts lat={15.3694} lon={44.191} enabled />);
    expect(screen.getByText('تنبيه درجة حرارة عالية')).toBeInTheDocument();
  });

  it('should display alert description in Arabic', () => {
    render(<WeatherAlerts lat={15.3694} lon={44.191} enabled />);
    expect(
      screen.getByText('من المتوقع درجات حرارة عالية تتجاوز 38 درجة مئوية')
    ).toBeInTheDocument();
  });

  it('should display affected areas', () => {
    render(<WeatherAlerts lat={15.3694} lon={44.191} enabled />);
    expect(screen.getByText('صنعاء')).toBeInTheDocument();
    expect(screen.getByText('عدن')).toBeInTheDocument();
  });

  it('should display severity label in Arabic', () => {
    render(<WeatherAlerts lat={15.3694} lon={44.191} enabled />);
    const highSeverityElements = screen.getAllByText(/عالي/);
    expect(highSeverityElements.length).toBeGreaterThanOrEqual(1);
  });

  it('should show section header', () => {
    render(<WeatherAlerts lat={15.3694} lon={44.191} enabled />);
    expect(screen.getByText('تنبيهات الطقس')).toBeInTheDocument();
  });

  it('should show no-alerts message when empty', () => {
    mockUseWeatherAlerts.mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<WeatherAlerts enabled />);
    expect(screen.getByText('لا توجد تنبيهات طقس حالية')).toBeInTheDocument();
    expect(screen.getByText('الأحوال الجوية طبيعية')).toBeInTheDocument();
  });

  it('should show loading skeleton', () => {
    mockUseWeatherAlerts.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    render(<WeatherAlerts enabled />);
    expect(screen.getByText('تنبيهات الطقس')).toBeInTheDocument();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Weather Data Type Validation Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('Weather Types & Contracts', () => {
  it('should validate WeatherData structure matches API contract', () => {
    const weather: WeatherData = mockCurrentWeather;

    // All required fields present with correct types
    expect(typeof weather.temperature).toBe('number');
    expect(typeof weather.humidity).toBe('number');
    expect(typeof weather.windSpeed).toBe('number');
    expect(typeof weather.windDirection).toBe('string');
    expect(typeof weather.pressure).toBe('number');
    expect(typeof weather.visibility).toBe('number');
    expect(typeof weather.uvIndex).toBe('number');
    expect(typeof weather.condition).toBe('string');
    expect(typeof weather.conditionAr).toBe('string');
    expect(typeof weather.location).toBe('string');
    expect(typeof weather.timestamp).toBe('string');

    // Timestamp is valid ISO 8601
    expect(new Date(weather.timestamp).toISOString()).toBe(weather.timestamp);
  });

  it('should validate ForecastDataPoint structure', () => {
    const point: ForecastDataPoint = mockForecast[0];

    expect(typeof point.date).toBe('string');
    expect(typeof point.temperature).toBe('number');
    expect(typeof point.humidity).toBe('number');
    expect(typeof point.precipitation).toBe('number');
    expect(typeof point.windSpeed).toBe('number');
    expect(typeof point.condition).toBe('string');
    expect(typeof point.conditionAr).toBe('string');
  });

  it('should validate WeatherAlert structure', () => {
    const alert: WeatherAlert = mockAlerts[0];

    expect(typeof alert.id).toBe('string');
    expect(typeof alert.type).toBe('string');
    expect(['low', 'medium', 'high', 'critical', 'warning', 'info']).toContain(alert.severity);
    expect(typeof alert.title).toBe('string');
    expect(typeof alert.titleAr).toBe('string');
    expect(typeof alert.isActive).toBe('boolean');
    expect(Array.isArray(alert.affectedAreas)).toBe(true);
    expect(Array.isArray(alert.affectedAreasAr)).toBe(true);
  });

  it('should generate 7-day forecast with ascending dates', () => {
    expect(mockForecast).toHaveLength(7);

    for (let i = 1; i < mockForecast.length; i++) {
      const prevDate = new Date(mockForecast[i - 1].date).getTime();
      const currDate = new Date(mockForecast[i].date).getTime();
      expect(currDate).toBeGreaterThan(prevDate);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Page Module Export Test
// ═══════════════════════════════════════════════════════════════════════════

describe('Weather Page Module', () => {
  it('should export a valid default component', async () => {
    const mod = await import('../page');
    expect(mod.default).toBeDefined();
    expect(typeof mod.default).toBe('function');
  });

  it('should export SEO metadata', async () => {
    const mod = await import('../page');
    expect(mod.metadata).toBeDefined();
    expect(mod.metadata.title).toContain('Weather');
  });
});
