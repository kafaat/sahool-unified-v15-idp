/**
 * SAHOOL React Hooks for API
 * Custom hooks for data fetching with SWR
 */

import useSWR, { SWRConfiguration } from 'swr';
import { apiClient } from './client';

// ═══════════════════════════════════════════════════════════════════════════
// Field Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useFields(tenantId: string, options?: SWRConfiguration) {
  return useSWR(
    tenantId ? ['fields', tenantId] : null,
    () => apiClient.getFields(tenantId),
    {
      revalidateOnFocus: false,
      ...options,
    }
  );
}

export function useField(fieldId: string, options?: SWRConfiguration) {
  return useSWR(
    fieldId ? ['field', fieldId] : null,
    () => apiClient.getField(fieldId),
    {
      revalidateOnFocus: false,
      ...options,
    }
  );
}

export function useNearbyFields(
  lat: number | null,
  lng: number | null,
  radius: number = 5000,
  options?: SWRConfiguration
) {
  return useSWR(
    lat && lng ? ['nearbyFields', lat, lng, radius] : null,
    () => apiClient.getNearbyFields(lat!, lng!, radius),
    {
      revalidateOnFocus: false,
      ...options,
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useFieldNdvi(fieldId: string, options?: SWRConfiguration) {
  return useSWR(
    fieldId ? ['fieldNdvi', fieldId] : null,
    () => apiClient.getFieldNdvi(fieldId),
    {
      revalidateOnFocus: false,
      refreshInterval: 60000, // Refresh every minute
      ...options,
    }
  );
}

export function useNdviSummary(tenantId: string, options?: SWRConfiguration) {
  return useSWR(
    tenantId ? ['ndviSummary', tenantId] : null,
    () => apiClient.getNdviSummary(tenantId),
    {
      revalidateOnFocus: false,
      ...options,
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useWeather(
  lat: number | null,
  lng: number | null,
  options?: SWRConfiguration
) {
  return useSWR(
    lat && lng ? ['weather', lat, lng] : null,
    () => apiClient.getWeather(lat!, lng!),
    {
      revalidateOnFocus: false,
      refreshInterval: 300000, // Refresh every 5 minutes
      ...options,
    }
  );
}

export function useWeatherForecast(
  lat: number | null,
  lng: number | null,
  days: number = 7,
  options?: SWRConfiguration
) {
  return useSWR(
    lat && lng ? ['weatherForecast', lat, lng, days] : null,
    () => apiClient.getWeatherForecast(lat!, lng!, days),
    {
      revalidateOnFocus: false,
      refreshInterval: 3600000, // Refresh every hour
      ...options,
    }
  );
}

export function useAgriculturalRisks(
  lat: number | null,
  lng: number | null,
  options?: SWRConfiguration
) {
  return useSWR(
    lat && lng ? ['agriculturalRisks', lat, lng] : null,
    () => apiClient.getAgriculturalRisks(lat!, lng!),
    {
      revalidateOnFocus: false,
      ...options,
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// IoT Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useSensorData(fieldId: string, options?: SWRConfiguration) {
  return useSWR(
    fieldId ? ['sensorData', fieldId] : null,
    () => apiClient.getSensorData(fieldId),
    {
      revalidateOnFocus: false,
      refreshInterval: 30000, // Refresh every 30 seconds
      ...options,
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useIrrigationRecommendation(
  fieldId: string,
  options?: SWRConfiguration
) {
  return useSWR(
    fieldId ? ['irrigationRecommendation', fieldId] : null,
    () => apiClient.getIrrigationRecommendation(fieldId),
    {
      revalidateOnFocus: false,
      ...options,
    }
  );
}
