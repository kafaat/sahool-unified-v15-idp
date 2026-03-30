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

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { hydrologyApi } from '../api';
import type {
  HydrologyAnalysisResult,
  HydrologyAnalysisParams,
  DrainageAnalysis,
  DrainageParams,
  WetnessAnalysis,
  WetnessParams,
  DepressionAnalysis,
  DepressionParams,
  StreamNetwork,
  StreamParams,
  BasinDelineation,
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
 * Triggers server-side drainage network extraction using D8 algorithm.
 *
 * @returns Mutation result with drainage network data
 */
export function useGetDrainage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, params }: { fieldId: string; params?: DrainageParams }) =>
      hydrologyApi.getDrainage(fieldId, params),
    onSuccess: (_result: DrainageAnalysis, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.drainage(fieldId) });
    },
  });
}

/**
 * Hook to get wetness/waterlogging analysis for a field.
 * خطاف للحصول على تحليل الرطوبة والتشبع المائي للحقل
 *
 * Calculates Topographic Wetness Index (TWI) and identifies
 * areas prone to waterlogging.
 *
 * @returns Mutation result with wetness analysis data
 */
export function useGetWetness() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, params }: { fieldId: string; params?: WetnessParams }) =>
      hydrologyApi.getWetness(fieldId, params),
    onSuccess: (_result: WetnessAnalysis, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.wetness(fieldId) });
    },
  });
}

/**
 * Hook to identify depressions/sinks in the field.
 * خطاف لتحديد المنخفضات في الحقل
 *
 * Detects terrain depressions that may cause waterlogging
 * and provides drainage recommendations.
 *
 * @returns Mutation result with depression analysis data
 */
export function useGetDepressions() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, params }: { fieldId: string; params?: DepressionParams }) =>
      hydrologyApi.getDepressions(fieldId, params),
    onSuccess: (_result: DepressionAnalysis, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.depressions(fieldId) });
    },
  });
}

/**
 * Hook to detect streams in the field.
 * خطاف لكشف المجاري المائية في الحقل
 *
 * Uses Strahler ordering to classify streams by importance.
 *
 * @returns Mutation result with stream network data
 */
export function useGetStreams() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, params }: { fieldId: string; params?: StreamParams }) =>
      hydrologyApi.getStreams(fieldId, params),
    onSuccess: (_result: StreamNetwork, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.streams(fieldId) });
    },
  });
}

/**
 * Hook to delineate drainage basins/watersheds.
 * خطاف لتحديد أحواض التصريف
 *
 * Identifies watershed boundaries and calculates
 * basin morphometric parameters.
 *
 * @returns Mutation result with basin delineation data
 */
export function useGetBasins() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, params }: { fieldId: string; params?: BasinParams }) =>
      hydrologyApi.getBasins(fieldId, params),
    onSuccess: (_result: BasinDelineation, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: hydrologyKeys.basins(fieldId) });
    },
  });
}
