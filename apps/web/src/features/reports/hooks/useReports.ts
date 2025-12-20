/**
 * Reports Feature - React Hooks
 * خطافات React لميزة التقارير
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  reportsApi,
  type Report,
  type GenerateReportRequest,
  type ReportFilters,
  type ReportTemplate,
} from '../api';

// Query Keys
const REPORTS_KEYS = {
  all: ['reports'] as const,
  list: (filters?: ReportFilters) => [...REPORTS_KEYS.all, 'list', filters] as const,
  detail: (id: string) => [...REPORTS_KEYS.all, 'detail', id] as const,
  templates: () => [...REPORTS_KEYS.all, 'templates'] as const,
  stats: () => [...REPORTS_KEYS.all, 'stats'] as const,
  scheduled: () => [...REPORTS_KEYS.all, 'scheduled'] as const,
};

/**
 * Hook to fetch reports list
 */
export function useReports(filters?: ReportFilters) {
  return useQuery({
    queryKey: REPORTS_KEYS.list(filters),
    queryFn: () => reportsApi.getReports(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch a single report
 */
export function useReport(id: string) {
  return useQuery({
    queryKey: REPORTS_KEYS.detail(id),
    queryFn: () => reportsApi.getReport(id),
    enabled: !!id,
    // Poll for status updates if report is generating
    refetchInterval: (query) => {
      const report = query.state.data as Report | undefined;
      if (report?.status === 'generating' || report?.status === 'pending') {
        return 5000; // Poll every 5 seconds
      }
      return false;
    },
  });
}

/**
 * Hook to generate a new report
 */
export function useGenerateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: GenerateReportRequest) => reportsApi.generateReport(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORTS_KEYS.all });
    },
  });
}

/**
 * Hook to get download URL
 */
export function useReportDownload(id: string) {
  return useQuery({
    queryKey: [...REPORTS_KEYS.detail(id), 'download'],
    queryFn: () => reportsApi.getDownloadUrl(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to delete a report
 */
export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => reportsApi.deleteReport(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: REPORTS_KEYS.list() });
      queryClient.removeQueries({ queryKey: REPORTS_KEYS.detail(id) });
    },
  });
}

/**
 * Hook to fetch report templates
 */
export function useReportTemplates() {
  return useQuery({
    queryKey: REPORTS_KEYS.templates(),
    queryFn: () => reportsApi.getTemplates(),
    staleTime: 30 * 60 * 1000, // 30 minutes - templates don't change often
  });
}

/**
 * Hook to fetch report statistics
 */
export function useReportStats() {
  return useQuery({
    queryKey: REPORTS_KEYS.stats(),
    queryFn: () => reportsApi.getStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to schedule a recurring report
 */
export function useScheduleReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: GenerateReportRequest & { schedule: string; recipients: string[] }) =>
      reportsApi.scheduleReport(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORTS_KEYS.scheduled() });
    },
  });
}

/**
 * Hook to fetch scheduled reports
 */
export function useScheduledReports() {
  return useQuery({
    queryKey: REPORTS_KEYS.scheduled(),
    queryFn: () => reportsApi.getScheduledReports(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
