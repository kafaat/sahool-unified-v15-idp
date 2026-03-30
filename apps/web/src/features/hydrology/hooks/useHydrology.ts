/**
 * Hydrology Feature - React Hooks
 * خطافات React لميزة تحليل الهيدرولوجيا
 *
 * React Query hooks for full hydrology analysis, drainage network,
 * wetness analysis, depression identification, stream detection,
 * and basin delineation.
 * خطافات لتحليل الهيدرولوجيا الكامل، شبكة التصريف،
 * تحليل الرطوبة، تحديد المنخفضات، كشف المجاري المائية،
 * وتحديد الأحواض.
 */

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { hydrologyApi } from '../api';
import type {
  HydrologyAnalysisResult,
  HydrologyAnalysisParams,
  DrainageParams,
  WetnessParams,
  DepressionParams,
  StreamParams,
  BasinParams,
} from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys - مفاتيح الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

export const hydrologyKeys = {
  all: ['hydrology'] as const,
  analysis: (fieldId: string) => [...hydrologyKeys.all, 'analysis', fieldId] as const,
  drainage: (fieldId: string) => [...hydrologyKeys.all, 'drainage', fieldId] as const,
  wetness: (fieldId: string) => [...hydrologyKeys.all, 'wetness', fieldId] as const,
  depressions: (fieldId: string) => [...hydrologyKeys.all, 'depressions', fieldId] as const,
  streams: (fieldId: string) => [...hydrologyKeys.all, 'streams', fieldId] as const,
  basins: (fieldId: string) => [...hydrologyKeys.all, 'basins', fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to run full hydrology analysis for a field.
 * خطاف لتشغيل تحليل هيدرولوجي كامل للحقل
 *
 * Triggers server-side hydrology analysis including drainage, wetness,
 * depressions, streams, and basin delineation.
 *
 * @returns Mutation result with full hydrology analysis data
 */
export function useAnalyzeHydrology() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: HydrologyAnalysisParams) =>
      hydrologyApi.analyzeHydrology(params),
    onSuccess: (_result: HydrologyAnalysisResult, params) => {
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.analysis(params.fieldId) });
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.drainage(params.fieldId) });
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.wetness(params.fieldId) });
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.depressions(params.fieldId) });
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.streams(params.fieldId) });
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.basins(params.fieldId) });
    },
  });
}

/**
 * Hook to get drainage network for a field.
 * خطاف للحصول على شبكة التصريف للحقل
 *
 * Fetches drainage network using D8 algorithm.
 *
 * @param fieldId - The field ID (pass undefined to disable)
 * @param params - Optional drainage parameters
 * @returns Query result with drainage network data
 */
export function useGetDrainage(fieldId: string | undefined, params?: DrainageParams) {
  return useQuery({
    queryKey: hydrologyKeys.drainage(fieldId!),
    queryFn: () => hydrologyApi.getDrainage(fieldId!, params),
    enabled: !!fieldId,
  });
}

/**
 * Hook to get wetness/waterlogging analysis for a field.
 * خطاف للحصول على تحليل الرطوبة والتشبع المائي للحقل
 *
 * Calculates Topographic Wetness Index (TWI) and identifies
 * areas prone to waterlogging.
 *
 * @param fieldId - The field ID (pass undefined to disable)
 * @param params - Optional wetness parameters
 * @returns Query result with wetness analysis data
 */
export function useGetWetness(fieldId: string | undefined, params?: WetnessParams) {
  return useQuery({
    queryKey: hydrologyKeys.wetness(fieldId!),
    queryFn: () => hydrologyApi.getWetness(fieldId!, params),
    enabled: !!fieldId,
  });
}

/**
 * Hook to identify depressions/sinks in the field.
 * خطاف لتحديد المنخفضات في الحقل
 *
 * Detects terrain depressions that may cause waterlogging
 * and provides drainage recommendations.
 *
 * @param fieldId - The field ID (pass undefined to disable)
 * @param params - Optional depression parameters
 * @returns Query result with depression analysis data
 */
export function useGetDepressions(fieldId: string | undefined, params?: DepressionParams) {
  return useQuery({
    queryKey: hydrologyKeys.depressions(fieldId!),
    queryFn: () => hydrologyApi.getDepressions(fieldId!, params),
    enabled: !!fieldId,
  });
}

/**
 * Hook to detect streams in the field.
 * خطاف لكشف المجاري المائية في الحقل
 *
 * Uses Strahler ordering to classify streams by importance.
 *
 * @param fieldId - The field ID (pass undefined to disable)
 * @param params - Optional stream parameters
 * @returns Query result with stream network data
 */
export function useGetStreams(fieldId: string | undefined, params?: StreamParams) {
  return useQuery({
    queryKey: hydrologyKeys.streams(fieldId!),
    queryFn: () => hydrologyApi.getStreams(fieldId!, params),
    enabled: !!fieldId,
  });
}

/**
 * Hook to delineate drainage basins/watersheds.
 * خطاف لتحديد أحواض التصريف
 *
 * Identifies watershed boundaries and calculates
 * basin morphometric parameters.
 *
 * @param fieldId - The field ID (pass undefined to disable)
 * @param params - Optional basin parameters
 * @returns Query result with basin delineation data
 */
export function useGetBasins(fieldId: string | undefined, params?: BasinParams) {
  return useQuery({
    queryKey: hydrologyKeys.basins(fieldId!),
    queryFn: () => hydrologyApi.getBasins(fieldId!, params),
    enabled: !!fieldId,
  });
}
