/**
 * SAHOOL React Hooks for API
 * Custom hooks for data fetching with SWR
 */

import useSWR, { SWRConfiguration } from 'swr';
import { apiClient } from './client';
import type {
  Field,
  NdviData,
  NdviSummary,
  WeatherData,
  WeatherForecast,
  AgriculturalRisk,
  Sensor,
  IrrigationRecommendation,
} from './types';

// Default SWR configuration with error handling and retry
const defaultConfig: SWRConfiguration = {
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  shouldRetryOnError: true,
  errorRetryCount: 3,
  errorRetryInterval: 5000,
  dedupingInterval: 2000, // Prevent duplicate requests within 2 seconds
  onError: (error) => {
    // Log errors for monitoring (can be replaced with error tracking service)
    console.error('API Error:', error);
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Field Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useFields(tenantId: string | null, options?: SWRConfiguration) {
  return useSWR<Field[]>(
    tenantId ? ['fields', tenantId] : null,
    async () => {
      if (!tenantId) return [];
      const response = await apiClient.getFields(tenantId);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch fields');
      }
      return response.data || [];
    },
    {
      ...defaultConfig,
      ...options,
    }
  );
}

export function useField(fieldId: string | null, options?: SWRConfiguration) {
  return useSWR<Field>(
    fieldId ? ['field', fieldId] : null,
    async () => {
      if (!fieldId) throw new Error('Field ID is required');
      const response = await apiClient.getField(fieldId);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch field');
      }
      return response.data;
    },
    {
      ...defaultConfig,
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
  return useSWR<Field[]>(
    lat && lng ? ['nearbyFields', lat, lng, radius] : null,
    async () => {
      if (!lat || !lng) return [];
      const response = await apiClient.getNearbyFields(lat, lng, radius);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch nearby fields');
      }
      return response.data || [];
    },
    {
      ...defaultConfig,
      ...options,
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useFieldNdvi(fieldId: string | null, options?: SWRConfiguration) {
  return useSWR<NdviData>(
    fieldId ? ['fieldNdvi', fieldId] : null,
    async () => {
      if (!fieldId) throw new Error('Field ID is required');
      const response = await apiClient.getFieldNdvi(fieldId);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch NDVI data');
      }
      return response.data;
    },
    {
      ...defaultConfig,
      refreshInterval: 60000, // Refresh every minute
      ...options,
    }
  );
}

export function useNdviSummary(tenantId: string | null, options?: SWRConfiguration) {
  return useSWR<NdviSummary>(
    tenantId ? ['ndviSummary', tenantId] : null,
    async () => {
      if (!tenantId) throw new Error('Tenant ID is required');
      const response = await apiClient.getNdviSummary(tenantId);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch NDVI summary');
      }
      return response.data;
    },
    {
      ...defaultConfig,
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
  return useSWR<WeatherData>(
    lat && lng ? ['weather', lat, lng] : null,
    async () => {
      if (!lat || !lng) throw new Error('Coordinates are required');
      const response = await apiClient.getWeather(lat, lng);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch weather data');
      }
      return response.data;
    },
    {
      ...defaultConfig,
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
  return useSWR<WeatherForecast>(
    lat && lng ? ['weatherForecast', lat, lng, days] : null,
    async () => {
      if (!lat || !lng) throw new Error('Coordinates are required');
      const response = await apiClient.getWeatherForecast(lat, lng, days);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch weather forecast');
      }
      return response.data;
    },
    {
      ...defaultConfig,
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
  return useSWR<AgriculturalRisk[]>(
    lat && lng ? ['agriculturalRisks', lat, lng] : null,
    async () => {
      if (!lat || !lng) throw new Error('Coordinates are required');
      const response = await apiClient.getAgriculturalRisks(lat, lng);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch agricultural risks');
      }
      return response.data || [];
    },
    {
      ...defaultConfig,
      ...options,
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// IoT Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useSensorData(fieldId: string | null, options?: SWRConfiguration) {
  return useSWR<Sensor[]>(
    fieldId ? ['sensorData', fieldId] : null,
    async () => {
      if (!fieldId) throw new Error('Field ID is required');
      const response = await apiClient.getSensorData(fieldId);
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch sensor data');
      }
      return response.data || [];
    },
    {
      ...defaultConfig,
      refreshInterval: 30000, // Refresh every 30 seconds
      ...options,
    }
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Hooks
// ═══════════════════════════════════════════════════════════════════════════

export function useIrrigationRecommendation(
  fieldId: string | null,
  options?: SWRConfiguration
) {
  return useSWR<IrrigationRecommendation>(
    fieldId ? ['irrigationRecommendation', fieldId] : null,
    async () => {
      if (!fieldId) throw new Error('Field ID is required');
      const response = await apiClient.getIrrigationRecommendation(fieldId);
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch irrigation recommendation');
      }
      return response.data;
    },
    {
      ...defaultConfig,
      ...options,
    }
  );
}
