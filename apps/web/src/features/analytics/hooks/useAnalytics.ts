/**
 * Analytics Feature - React Hooks
 * خطافات React لميزة التحليلات
 */

'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import type {
  YieldData,
  CostData,
  RevenueData,
  KPIMetric,
  ComparisonData,
  AnalyticsFilters,
  AnalyticsSummary,
  ResourceUsage,
  ReportConfig,
  ComparisonType,
  MetricType,
} from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Query Keys
const ANALYTICS_KEYS = {
  all: ['analytics'] as const,
  summary: (filters?: AnalyticsFilters) => [...ANALYTICS_KEYS.all, 'summary', filters] as const,
  yield: (filters?: AnalyticsFilters) => [...ANALYTICS_KEYS.all, 'yield', filters] as const,
  cost: (filters?: AnalyticsFilters) => [...ANALYTICS_KEYS.all, 'cost', filters] as const,
  revenue: (filters?: AnalyticsFilters) => [...ANALYTICS_KEYS.all, 'revenue', filters] as const,
  kpis: (filters?: AnalyticsFilters) => [...ANALYTICS_KEYS.all, 'kpis', filters] as const,
  comparison: (type: ComparisonType, metric: MetricType, filters?: AnalyticsFilters) =>
    [...ANALYTICS_KEYS.all, 'comparison', type, metric, filters] as const,
  resources: (filters?: AnalyticsFilters) => [...ANALYTICS_KEYS.all, 'resources', filters] as const,
};

/**
 * Hook to fetch analytics summary
 */
export function useAnalyticsSummary(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.summary(filters),
    queryFn: async (): Promise<AnalyticsSummary> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.period) params.set('period', filters.period);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);
      if (filters?.seasons?.length) params.set('seasons', filters.seasons.join(','));

      const response = await api.get(`/v1/analytics/summary?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch yield analysis data
 */
export function useYieldAnalysis(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.yield(filters),
    queryFn: async (): Promise<YieldData[]> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.period) params.set('period', filters.period);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);
      if (filters?.seasons?.length) params.set('seasons', filters.seasons.join(','));

      const response = await api.get(`/v1/analytics/yield?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch cost analysis data
 */
export function useCostAnalysis(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.cost(filters),
    queryFn: async (): Promise<CostData[]> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.period) params.set('period', filters.period);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);

      const response = await api.get(`/v1/analytics/cost?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch revenue and profit data
 */
export function useRevenueAnalysis(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.revenue(filters),
    queryFn: async (): Promise<RevenueData[]> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.period) params.set('period', filters.period);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);

      const response = await api.get(`/v1/analytics/revenue?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch KPI metrics
 */
export function useKPIMetrics(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.kpis(filters),
    queryFn: async (): Promise<KPIMetric[]> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.period) params.set('period', filters.period);
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);

      const response = await api.get(`/v1/analytics/kpis?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch comparison data
 */
export function useComparison(
  type: ComparisonType,
  metric: MetricType,
  filters?: AnalyticsFilters
) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.comparison(type, metric, filters),
    queryFn: async (): Promise<ComparisonData> => {
      const params = new URLSearchParams();
      params.set('type', type);
      params.set('metric', metric);
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.seasons?.length) params.set('seasons', filters.seasons.join(','));
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);

      const response = await api.get(`/v1/analytics/comparison?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch resource usage data
 */
export function useResourceUsage(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.resources(filters),
    queryFn: async (): Promise<ResourceUsage[]> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.startDate) params.set('start_date', filters.startDate);
      if (filters?.endDate) params.set('end_date', filters.endDate);

      const response = await api.get(`/v1/analytics/resources?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to generate a report
 */
export function useGenerateReport() {
  return useMutation({
    mutationFn: async (config: ReportConfig): Promise<{ downloadUrl: string; reportId: string }> => {
      const response = await api.post('/v1/analytics/reports/generate', config);
      return response.data;
    },
  });
}

/**
 * Hook to download a generated report
 */
export function useDownloadReport() {
  return useMutation({
    mutationFn: async (reportId: string): Promise<Blob> => {
      const response = await api.get(`/v1/analytics/reports/${reportId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    },
  });
}
