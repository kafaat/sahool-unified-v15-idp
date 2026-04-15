/**
 * SAHOOL Weather Data Hook
 * خطاف بيانات الطقس
 */

import { useQuery } from '@tanstack/react-query';
import { dashboardApi, type DashboardData } from '../api';

export type WeatherData = DashboardData['weather'];

interface UseWeatherOptions {
  /** Enable/disable the query */
  enabled?: boolean;
}

/**
 * Hook for fetching weather data independently for the dashboard
 * @param options - Configuration options
 */
export function useWeather(options: UseWeatherOptions = {}) {
  const { enabled = true } = options;

  return useQuery({
    queryKey: ['dashboard', 'weather'],
    queryFn: dashboardApi.getWeather,
    staleTime: 5 * 60 * 1000, // 5 minutes - weather doesn't change rapidly
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
    enabled,
  });
}
