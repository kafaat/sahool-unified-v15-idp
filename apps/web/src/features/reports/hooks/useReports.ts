/**
 * Reports Feature - React Hooks (Extended)
 * خطافات React لميزة التقارير (موسعة)
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { logger } from "@/lib/logger";
import {
  reportsApi,
  type Report,
  type GenerateReportRequest,
  type ReportFilters,
} from "../api";
import { reportsApi as fieldReportsApi } from "../api/reports-api";
import type {
  GenerateFieldReportRequest,
  GenerateSeasonReportRequest,
  ReportHistoryFilters,
  ShareReportRequest,
  GeneratedReport,
} from "../types/reports";

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

const REPORTS_KEYS = {
  all: ["reports"] as const,
  list: (filters?: ReportFilters) =>
    [...REPORTS_KEYS.all, "list", filters] as const,
  detail: (id: string) => [...REPORTS_KEYS.all, "detail", id] as const,
  templates: () => [...REPORTS_KEYS.all, "templates"] as const,
  stats: () => [...REPORTS_KEYS.all, "stats"] as const,
  scheduled: () => [...REPORTS_KEYS.all, "scheduled"] as const,
  history: (filters?: ReportHistoryFilters) =>
    [...REPORTS_KEYS.all, "history", filters] as const,
  fieldData: (fieldId: string, startDate?: string, endDate?: string) =>
    [...REPORTS_KEYS.all, "fieldData", fieldId, startDate, endDate] as const,
  seasonData: (
    fieldId: string,
    season?: string,
    startDate?: string,
    endDate?: string,
  ) =>
    [
      ...REPORTS_KEYS.all,
      "seasonData",
      fieldId,
      season,
      startDate,
      endDate,
    ] as const,
  status: (id: string) => [...REPORTS_KEYS.all, "status", id] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Legacy Hooks (from original api.ts)
// ═══════════════════════════════════════════════════════════════════════════

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
      if (report?.status === "generating" || report?.status === "pending") {
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
    mutationFn: (request: GenerateReportRequest) =>
      reportsApi.generateReport(request),
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
    queryKey: [...REPORTS_KEYS.detail(id), "download"],
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
    mutationFn: (
      request: GenerateReportRequest & {
        schedule: string;
        recipients: string[];
      },
    ) => reportsApi.scheduleReport(request),
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

// ═══════════════════════════════════════════════════════════════════════════
// Extended Field Report Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to generate a field report
 * خطاف لإنشاء تقرير حقل
 */
export function useGenerateFieldReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: GenerateFieldReportRequest) =>
      fieldReportsApi.generateFieldReport(request),
    onSuccess: (data: GeneratedReport) => {
      queryClient.invalidateQueries({ queryKey: REPORTS_KEYS.history() });
      queryClient.setQueryData(REPORTS_KEYS.detail(data.id), data);
      logger.info("Field report generated successfully:", data.id);
    },
    onError: (error) => {
      logger.error("Failed to generate field report:", error);
    },
  });
}

/**
 * Hook to generate a season report
 * خطاف لإنشاء تقرير موسم
 */
export function useGenerateSeasonReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: GenerateSeasonReportRequest) =>
      fieldReportsApi.generateSeasonReport(request),
    onSuccess: (data: GeneratedReport) => {
      queryClient.invalidateQueries({ queryKey: REPORTS_KEYS.history() });
      queryClient.setQueryData(REPORTS_KEYS.detail(data.id), data);
      logger.info("Season report generated successfully:", data.id);
    },
    onError: (error) => {
      logger.error("Failed to generate season report:", error);
    },
  });
}

/**
 * Hook to fetch report history
 * خطاف لجلب سجل التقارير
 */
export function useReportHistory(filters?: ReportHistoryFilters) {
  return useQuery({
    queryKey: REPORTS_KEYS.history(filters),
    queryFn: () => fieldReportsApi.getReportHistory(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to download a report
 * خطاف لتنزيل تقرير
 */
export function useDownloadReport() {
  return useMutation({
    mutationFn: async (reportId: string) => {
      const response = await fieldReportsApi.downloadReport(reportId);
      if (response.url) {
        // Trigger download
        window.open(response.url, "_blank");
      }
      return response;
    },
    onError: (error) => {
      logger.error("Failed to download report:", error);
    },
  });
}

/**
 * Hook to share a report
 * خطاف لمشاركة تقرير
 */
export function useShareReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ShareReportRequest) =>
      fieldReportsApi.shareReport(request),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: REPORTS_KEYS.detail(variables.reportId),
      });
      logger.info("Report shared successfully:", variables.reportId);
    },
    onError: (error) => {
      logger.error("Failed to share report:", error);
    },
  });
}

/**
 * Hook to delete a field report
 * خطاف لحذف تقرير حقل
 */
export function useDeleteFieldReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reportId: string) => fieldReportsApi.deleteReport(reportId),
    onSuccess: (_, reportId) => {
      queryClient.invalidateQueries({ queryKey: REPORTS_KEYS.history() });
      queryClient.removeQueries({ queryKey: REPORTS_KEYS.detail(reportId) });
      logger.info("Report deleted successfully:", reportId);
    },
    onError: (error) => {
      logger.error("Failed to delete report:", error);
    },
  });
}

/**
 * Hook to fetch field report data
 * خطاف لجلب بيانات تقرير الحقل
 */
export function useFieldReportData(
  fieldId: string,
  startDate?: string,
  endDate?: string,
) {
  return useQuery({
    queryKey: REPORTS_KEYS.fieldData(fieldId, startDate, endDate),
    queryFn: () =>
      fieldReportsApi.getFieldReportData(fieldId, startDate, endDate),
    enabled: !!fieldId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch season report data
 * خطاف لجلب بيانات تقرير الموسم
 */
export function useSeasonReportData(
  fieldId: string,
  season?: string,
  startDate?: string,
  endDate?: string,
) {
  return useQuery({
    queryKey: REPORTS_KEYS.seasonData(fieldId, season, startDate, endDate),
    queryFn: () =>
      fieldReportsApi.getSeasonReportData(fieldId, season, startDate, endDate),
    enabled: !!fieldId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to check report generation status with polling
 * خطاف للتحقق من حالة إنشاء التقرير مع التحديث الدوري
 */
export function useReportStatus(reportId: string, enabled = true) {
  return useQuery({
    queryKey: REPORTS_KEYS.status(reportId),
    queryFn: () => fieldReportsApi.checkReportStatus(reportId),
    enabled: !!reportId && enabled,
    refetchInterval: (query) => {
      const report = query.state.data as GeneratedReport | undefined;
      if (report?.status === "generating" || report?.status === "pending") {
        return 3000; // Poll every 3 seconds while generating
      }
      return false; // Stop polling when ready, failed, or expired
    },
  });
}

/**
 * Hook to get field report templates
 * خطاف لجلب قوالب تقارير الحقول
 */
export function useFieldReportTemplates() {
  return useQuery({
    queryKey: [...REPORTS_KEYS.templates(), "field"],
    queryFn: () => fieldReportsApi.getReportTemplates(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}
