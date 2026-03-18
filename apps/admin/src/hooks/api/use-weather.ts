/**
 * SAHOOL Admin - Weather data hooks
 * خطافات بيانات الطقس
 *
 * Hooks for weather-service and weather-core endpoints.
 */

"use client";

import { useApiQuery } from "./use-api-query";
import {
  getWeatherCurrent,
  getWeatherForecast,
  getAgriculturalReport,
  getWeatherByLocation,
  getWeatherForecastByLocation,
  getWeatherLocations,
  fetchWeatherAlerts,
} from "@/lib/api";

/**
 * Current weather by coordinates (weather-core, POST)
 */
export function useWeatherCurrent(
  lat: number,
  lon: number,
  fieldId?: string,
) {
  return useApiQuery(
    ["weather", "current", String(lat), String(lon)],
    () => getWeatherCurrent(lat, lon, fieldId),
    {
      enabled: !!lat && !!lon,
      refetchInterval: 300000, // 5 minutes
      staleTime: 120000,
    },
  );
}

/**
 * Weather forecast by coordinates
 */
export function useWeatherForecast(
  lat: number,
  lon: number,
  days: number = 7,
  fieldId?: string,
) {
  return useApiQuery(
    ["weather", "forecast", String(lat), String(lon), String(days)],
    () => getWeatherForecast(lat, lon, days, fieldId),
    {
      enabled: !!lat && !!lon,
      refetchInterval: 600000, // 10 minutes
      staleTime: 300000,
    },
  );
}

/**
 * Agricultural weather report
 */
export function useAgriculturalReport(
  lat: number,
  lon: number,
  fieldId?: string,
) {
  return useApiQuery(
    ["weather", "agricultural", String(lat), String(lon)],
    () => getAgriculturalReport(lat, lon, fieldId),
    {
      enabled: !!lat && !!lon,
      staleTime: 300000,
    },
  );
}

/**
 * Current weather by location ID (weather-service, GET)
 */
export function useWeatherByLocation(locationId: string) {
  return useApiQuery(
    ["weather", "location", locationId],
    () => getWeatherByLocation(locationId),
    {
      enabled: !!locationId,
      refetchInterval: 300000,
    },
  );
}

/**
 * Forecast by location ID
 */
export function useWeatherForecastByLocation(
  locationId: string,
  days: number = 7,
) {
  return useApiQuery(
    ["weather", "location-forecast", locationId, String(days)],
    () => getWeatherForecastByLocation(locationId, days),
    {
      enabled: !!locationId,
      staleTime: 300000,
    },
  );
}

/**
 * Available weather locations
 */
export function useWeatherLocations() {
  return useApiQuery(
    ["weather", "locations"],
    getWeatherLocations,
    { staleTime: 3600000 }, // 1 hour - locations rarely change
  );
}

/**
 * Weather alerts for a location
 */
export function useWeatherAlerts(locationId: string = "sanaa") {
  return useApiQuery(
    ["weather", "alerts", locationId],
    () => fetchWeatherAlerts(locationId),
    {
      enabled: !!locationId,
      refetchInterval: 300000,
    },
  );
}
