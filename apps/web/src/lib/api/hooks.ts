/**
 * SAHOOL React Hooks for API
 * Custom hooks for data fetching with React Query
 */

import { useQuery, UseQueryOptions } from "@tanstack/react-query";
import { apiClient } from "./client";
import type {
  Field,
  NdviData,
  NdviSummary,
  WeatherData,
  WeatherForecast,
  AgriculturalRisk,
  Sensor,
  IrrigationRecommendation,
} from "./types";

// Query Keys - Centralized key management for cache invalidation
export const apiQueryKeys = {
  fields: (tenantId: string | null) => ["fields", tenantId] as const,
  field: (fieldId: string | null) => ["field", fieldId] as const,
  nearbyFields: (lat: number | null, lng: number | null, radius: number) =>
    ["nearbyFields", lat, lng, radius] as const,
  fieldNdvi: (fieldId: string | null) => ["fieldNdvi", fieldId] as const,
  ndviSummary: (tenantId: string | null) => ["ndviSummary", tenantId] as const,
  weather: (lat: number | null, lng: number | null) =>
    ["weather", lat, lng] as const,
  weatherForecast: (lat: number | null, lng: number | null, days: number) =>
    ["weatherForecast", lat, lng, days] as const,
  agriculturalRisks: (lat: number | null, lng: number | null) =>
    ["agriculturalRisks", lat, lng] as const,
  sensorData: (fieldId: string | null) => ["sensorData", fieldId] as const,
  irrigationRecommendation: (fieldId: string | null) =>
    ["irrigationRecommendation", fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Field Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch all fields for a tenant
 * @param tenantId - Tenant ID to fetch fields for
 * @param options - React Query options
 */
export function useFields(
  tenantId: string | null,
  options?: Omit<UseQueryOptions<Field[], Error>, "queryKey" | "queryFn">,
) {
  return useQuery<Field[], Error>({
    queryKey: apiQueryKeys.fields(tenantId),
    queryFn: async () => {
      if (!tenantId) return [];
      const response = await apiClient.getFields(tenantId);
      if (!response.success) {
        throw new Error(response.error || "Failed to fetch fields");
      }
      return response.data || [];
    },
    enabled: !!tenantId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

/**
 * Hook to fetch a single field by ID
 * @param fieldId - Field ID to fetch
 * @param options - React Query options
 */
export function useField(
  fieldId: string | null,
  options?: Omit<UseQueryOptions<Field, Error>, "queryKey" | "queryFn">,
) {
  return useQuery<Field, Error>({
    queryKey: apiQueryKeys.field(fieldId),
    queryFn: async () => {
      if (!fieldId) throw new Error("Field ID is required");
      const response = await apiClient.getField(fieldId);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to fetch field");
      }
      return response.data;
    },
    enabled: !!fieldId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

/**
 * Hook to fetch nearby fields based on coordinates
 * @param lat - Latitude
 * @param lng - Longitude
 * @param radius - Search radius in meters (default: 5000)
 * @param options - React Query options
 */
export function useNearbyFields(
  lat: number | null,
  lng: number | null,
  radius: number = 5000,
  options?: Omit<UseQueryOptions<Field[], Error>, "queryKey" | "queryFn">,
) {
  return useQuery<Field[], Error>({
    queryKey: apiQueryKeys.nearbyFields(lat, lng, radius),
    queryFn: async () => {
      if (!lat || !lng) return [];
      const response = await apiClient.getNearbyFields(lat, lng, radius);
      if (!response.success) {
        throw new Error(response.error || "Failed to fetch nearby fields");
      }
      return response.data || [];
    },
    enabled: !!(lat && lng),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// NDVI Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch NDVI data for a specific field
 * @param fieldId - Field ID to fetch NDVI data for
 * @param options - React Query options
 */
export function useFieldNdvi(
  fieldId: string | null,
  options?: Omit<UseQueryOptions<NdviData, Error>, "queryKey" | "queryFn">,
) {
  return useQuery<NdviData, Error>({
    queryKey: apiQueryKeys.fieldNdvi(fieldId),
    queryFn: async () => {
      if (!fieldId) throw new Error("Field ID is required");
      const response = await apiClient.getFieldNdvi(fieldId);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to fetch NDVI data");
      }
      return response.data;
    },
    enabled: !!fieldId,
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 60000, // Refresh every minute for real-time updates
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

/**
 * Hook to fetch NDVI summary for a tenant
 * @param tenantId - Tenant ID to fetch NDVI summary for
 * @param options - React Query options
 */
export function useNdviSummary(
  tenantId: string | null,
  options?: Omit<UseQueryOptions<NdviSummary, Error>, "queryKey" | "queryFn">,
) {
  return useQuery<NdviSummary, Error>({
    queryKey: apiQueryKeys.ndviSummary(tenantId),
    queryFn: async () => {
      if (!tenantId) throw new Error("Tenant ID is required");
      const response = await apiClient.getNdviSummary(tenantId);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to fetch NDVI summary");
      }
      return response.data;
    },
    enabled: !!tenantId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Weather Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch current weather data for coordinates
 * @param lat - Latitude
 * @param lng - Longitude
 * @param options - React Query options
 */
export function useWeather(
  lat: number | null,
  lng: number | null,
  options?: Omit<UseQueryOptions<WeatherData, Error>, "queryKey" | "queryFn">,
) {
  return useQuery<WeatherData, Error>({
    queryKey: apiQueryKeys.weather(lat, lng),
    queryFn: async () => {
      if (!lat || !lng) throw new Error("Coordinates are required");
      const response = await apiClient.getWeather(lat, lng);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to fetch weather data");
      }
      return response.data;
    },
    enabled: !!(lat && lng),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 300000, // Refresh every 5 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

/**
 * Hook to fetch weather forecast for coordinates
 * @param lat - Latitude
 * @param lng - Longitude
 * @param days - Number of days to forecast (default: 7)
 * @param options - React Query options
 */
export function useWeatherForecast(
  lat: number | null,
  lng: number | null,
  days: number = 7,
  options?: Omit<
    UseQueryOptions<WeatherForecast, Error>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery<WeatherForecast, Error>({
    queryKey: apiQueryKeys.weatherForecast(lat, lng, days),
    queryFn: async () => {
      if (!lat || !lng) throw new Error("Coordinates are required");
      const response = await apiClient.getWeatherForecast(lat, lng, days);
      if (!response.success || !response.data) {
        throw new Error(response.error || "Failed to fetch weather forecast");
      }
      return response.data;
    },
    enabled: !!(lat && lng),
    staleTime: 60 * 60 * 1000, // 1 hour
    refetchInterval: 3600000, // Refresh every hour
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

/**
 * Hook to fetch agricultural risks for coordinates
 * @param lat - Latitude
 * @param lng - Longitude
 * @param options - React Query options
 */
export function useAgriculturalRisks(
  lat: number | null,
  lng: number | null,
  options?: Omit<
    UseQueryOptions<AgriculturalRisk[], Error>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery<AgriculturalRisk[], Error>({
    queryKey: apiQueryKeys.agriculturalRisks(lat, lng),
    queryFn: async () => {
      if (!lat || !lng) throw new Error("Coordinates are required");
      const response = await apiClient.getAgriculturalRisks(lat, lng);
      if (!response.success) {
        throw new Error(response.error || "Failed to fetch agricultural risks");
      }
      return response.data || [];
    },
    enabled: !!(lat && lng),
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// IoT Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch sensor data for a field
 * @param fieldId - Field ID to fetch sensor data for
 * @param options - React Query options
 */
export function useSensorData(
  fieldId: string | null,
  options?: Omit<UseQueryOptions<Sensor[], Error>, "queryKey" | "queryFn">,
) {
  return useQuery<Sensor[], Error>({
    queryKey: apiQueryKeys.sensorData(fieldId),
    queryFn: async () => {
      if (!fieldId) throw new Error("Field ID is required");
      const response = await apiClient.getSensorData(fieldId);
      if (!response.success) {
        throw new Error(response.error || "Failed to fetch sensor data");
      }
      return response.data || [];
    },
    enabled: !!fieldId,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30000, // Refresh every 30 seconds for real-time IoT data
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Irrigation Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch irrigation recommendation for a field
 * @param fieldId - Field ID to fetch irrigation recommendation for
 * @param options - React Query options
 */
export function useIrrigationRecommendation(
  fieldId: string | null,
  options?: Omit<
    UseQueryOptions<IrrigationRecommendation, Error>,
    "queryKey" | "queryFn"
  >,
) {
  return useQuery<IrrigationRecommendation, Error>({
    queryKey: apiQueryKeys.irrigationRecommendation(fieldId),
    queryFn: async () => {
      if (!fieldId) throw new Error("Field ID is required");
      const response = await apiClient.getIrrigationRecommendation(fieldId);
      if (!response.success || !response.data) {
        throw new Error(
          response.error || "Failed to fetch irrigation recommendation",
        );
      }
      return response.data;
    },
    enabled: !!fieldId,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    ...options,
  });
}
