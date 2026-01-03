/**
 * Analytics Feature - React Hooks
 * خطافات React لميزة التحليلات
 */

'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
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
import { analyticsApi } from '../api';

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
    queryFn: () => analyticsApi.getSummary(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch yield analysis data
 */
export function useYieldAnalysis(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.yield(filters),
    queryFn: () => analyticsApi.getYieldAnalytics(filters),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch cost analysis data
 */
export function useCostAnalysis(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.cost(filters),
    queryFn: () => analyticsApi.getCostAnalytics(filters),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch revenue and profit data
 */
export function useRevenueAnalysis(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.revenue(filters),
    queryFn: () => analyticsApi.getRevenueAnalytics(filters),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch KPI metrics
 */
export function useKPIMetrics(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.kpis(filters),
    queryFn: () => analyticsApi.getKPIs(filters),
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
    queryFn: () => analyticsApi.getComparison(type, metric, filters),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to fetch resource usage data
 */
export function useResourceUsage(filters?: AnalyticsFilters) {
  return useQuery({
    queryKey: ANALYTICS_KEYS.resources(filters),
    queryFn: () => analyticsApi.getResourceUsage(filters),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Hook to generate a report
 */
export function useGenerateReport() {
  return useMutation({
    mutationFn: (config: ReportConfig) => analyticsApi.generateReport(config),
  });
}

/**
 * Hook to download a generated report
 */
export function useDownloadReport() {
  return useMutation({
    mutationFn: (reportId: string) => analyticsApi.downloadReport(reportId),
  });
}
