/**
 * Tests for weather hooks
 * اختبارات خطافات الطقس
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { invalidateQueries } from '../use-api-query';

vi.mock('@/lib/api', () => ({
  getWeatherCurrent: vi.fn().mockResolvedValue({
    temperature: 28,
    humidity: 65,
    wind_speed: 12,
    description: 'Partly cloudy',
    description_ar: 'غائم جزئياً',
  }),
  getWeatherForecast: vi.fn().mockResolvedValue([
    { date: '2026-03-18', high: 32, low: 18 },
    { date: '2026-03-19', high: 30, low: 17 },
  ]),
  getAgriculturalReport: vi.fn().mockResolvedValue({
    et: 5.5,
    spray_window: true,
    frost_risk: false,
  }),
  getWeatherByLocation: vi.fn().mockResolvedValue({
    temperature: 25,
    humidity: 70,
  }),
  getWeatherForecastByLocation: vi
    .fn()
    .mockResolvedValue([{ date: '2026-03-18', high: 28, low: 15 }]),
  getWeatherLocations: vi.fn().mockResolvedValue({
    locations: [
      { id: 'sanaa', name: 'صنعاء' },
      { id: 'aden', name: 'عدن' },
    ],
  }),
  fetchWeatherAlerts: vi
    .fn()
    .mockResolvedValue([
      { id: 'a1', type: 'heat', severity: 'warning', message: 'High temperature expected' },
    ]),
}));

import {
  useWeatherCurrent,
  useWeatherForecast,
  useAgriculturalReport,
  useWeatherByLocation,
  useWeatherForecastByLocation,
  useWeatherLocations,
  useWeatherAlerts,
} from '../use-weather';

beforeEach(() => {
  invalidateQueries('');
});

describe('useWeatherCurrent', () => {
  it('fetches current weather by coordinates', async () => {
    const { result } = renderHook(() => useWeatherCurrent(15.37, 44.19));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(
      expect.objectContaining({
        temperature: 28,
        humidity: 65,
      })
    );
  });

  it('does not fetch without valid coordinates', () => {
    const { result } = renderHook(() => useWeatherCurrent(0, 0));
    expect(result.current.isLoading).toBe(false);
  });
});

describe('useWeatherForecast', () => {
  it('fetches forecast data', async () => {
    const { result } = renderHook(() => useWeatherForecast(15.37, 44.19, 7));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
  });
});

describe('useAgriculturalReport', () => {
  it('fetches agricultural weather report', async () => {
    const { result } = renderHook(() => useAgriculturalReport(15.37, 44.19));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(
      expect.objectContaining({
        et: 5.5,
        spray_window: true,
      })
    );
  });
});

describe('useWeatherByLocation', () => {
  it('fetches weather by location ID', async () => {
    const { result } = renderHook(() => useWeatherByLocation('sanaa'));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(expect.objectContaining({ temperature: 25 }));
  });

  it('does not fetch without location ID', () => {
    const { result } = renderHook(() => useWeatherByLocation(''));
    expect(result.current.isLoading).toBe(false);
  });
});

describe('useWeatherForecastByLocation', () => {
  it('fetches forecast by location', async () => {
    const { result } = renderHook(() => useWeatherForecastByLocation('sanaa'));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(1);
  });
});

describe('useWeatherLocations', () => {
  it('fetches available weather locations', async () => {
    const { result } = renderHook(() => useWeatherLocations());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.locations).toHaveLength(2);
  });
});

describe('useWeatherAlerts', () => {
  it('fetches weather alerts for a location', async () => {
    const { result } = renderHook(() => useWeatherAlerts('sanaa'));

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(1);
    expect(result.current.data?.[0]).toHaveProperty('type', 'heat');
  });
});
