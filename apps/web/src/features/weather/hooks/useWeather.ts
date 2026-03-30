/**
 * SAHOOL Weather Hook
 * خطاف الطقس
 *
 * Uses weatherApi from ../api.ts which wraps all calls with safeFetch.
 */

import { useQuery } from '@tanstack/react-query';
import { weatherApi } from '../api';

// ─────────────────────────────────────────────────────────────────────────────
// React Query Hooks
// ─────────────────────────────────────────────────────────────────────────────

export interface WeatherHookOptions {
  lat?: number;
  lon?: number;
  enabled?: boolean;
}

/**
 * Hook to fetch current weather data
 * @param options - Options including latitude, longitude, and enabled flag
 * @returns React Query result with current weather data
 */
export function useCurrentWeather(options?: WeatherHookOptions) {
  const { lat, lon, enabled = true } = options || {};

  return useQuery({
    queryKey: ['weather', 'current', lat, lon],
    queryFn: () => weatherApi.getCurrentWeather(lat, lon),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to fetch weather forecast
 * @param options - Options including latitude, longitude, days, and enabled flag
 * @returns React Query result with forecast data
 */
export function useWeatherForecast(options?: WeatherHookOptions & { days?: number }) {
  const { lat, lon, days = 7, enabled = true } = options || {};

  return useQuery({
    queryKey: ['weather', 'forecast', lat, lon, days],
    queryFn: () => weatherApi.getForecast(lat, lon, days),
    staleTime: 30 * 60 * 1000, // 30 minutes
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}

/**
 * Hook to fetch weather alerts
 * @param options - Options including latitude, longitude, and enabled flag
 * @returns React Query result with weather alerts
 */
export function useWeatherAlerts(options?: WeatherHookOptions) {
  const { lat, lon, enabled = true } = options || {};

  return useQuery({
    queryKey: ['weather', 'alerts', lat, lon],
    queryFn: () => weatherApi.getAlerts(lat, lon),
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchInterval: 15 * 60 * 1000, // Refetch every 15 minutes
    enabled,
    retry: 2,
    retryDelay: 1000,
  });
}
