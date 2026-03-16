/**
 * Terrain Feature - React Hooks
 * خطافات React لميزة تحليل التضاريس
 *
 * React Query hooks for DEM analysis, slope, aspect, drainage,
 * watershed, flow, leveling optimization, cut/fill, and cost estimation.
 * خطافات لتحليل نموذج الارتفاعات الرقمية، الميل، الاتجاه، الصرف،
 * مستجمعات المياه، التدفق، تحسين التسوية، القطع/الردم، وتقدير التكلفة.
 */

"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { terrainApi } from "../api";
import type {
  DEMAnalysis,
  SlopeAnalysis,
  AspectAnalysis,
  DrainageAnalysis,
  WatershedAnalysis,
  FlowAnalysis,
  LevelingPlan,
  CutFillResult,
  LevelingCost,
} from "../types";

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys - مفاتيح الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

export const terrainKeys = {
  all: ["terrain"] as const,
  dem: (fieldId: string) => [...terrainKeys.all, "dem", fieldId] as const,
  slope: (fieldId: string) => [...terrainKeys.all, "slope", fieldId] as const,
  aspect: (fieldId: string) => [...terrainKeys.all, "aspect", fieldId] as const,
  drainage: (fieldId: string) => [...terrainKeys.all, "drainage", fieldId] as const,
  watershed: (fieldId: string) => [...terrainKeys.all, "watershed", fieldId] as const,
  flow: (fieldId: string) => [...terrainKeys.all, "flow", fieldId] as const,
  leveling: (fieldId: string) => [...terrainKeys.all, "leveling", fieldId] as const,
  cutFill: (fieldId: string) => [...terrainKeys.all, "cutFill", fieldId] as const,
  cost: (fieldId: string) => [...terrainKeys.all, "cost", fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to analyze DEM (Digital Elevation Model) for a field
 * خطاف لتحليل نموذج الارتفاعات الرقمية للحقل
 *
 * Triggers server-side DEM analysis and returns elevation data.
 *
 * @returns Mutation result with DEM analysis data
 */
export function useAnalyzeDEM() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, data }: { fieldId: string; data?: FormData }) =>
      terrainApi.analyzeDEM(fieldId, data),
    onSuccess: (_result: DEMAnalysis, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.dem(fieldId) });
      queryClient.invalidateQueries({ queryKey: terrainKeys.slope(fieldId) });
      queryClient.invalidateQueries({ queryKey: terrainKeys.aspect(fieldId) });
    },
  });
}

/**
 * Hook to analyze slope for a field
 * خطاف لتحليل الميل للحقل
 *
 * Triggers server-side slope analysis based on DEM data.
 *
 * @returns Mutation result with slope analysis data
 */
export function useAnalyzeSlope() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => terrainApi.analyzeSlope(fieldId),
    onSuccess: (_result: SlopeAnalysis, fieldId) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.slope(fieldId) });
    },
  });
}

/**
 * Hook to analyze aspect (orientation) for a field
 * خطاف لتحليل الاتجاه للحقل
 *
 * Triggers server-side aspect analysis for sun exposure and drainage direction.
 *
 * @returns Mutation result with aspect analysis data
 */
export function useAnalyzeAspect() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => terrainApi.analyzeAspect(fieldId),
    onSuccess: (_result: AspectAnalysis, fieldId) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.aspect(fieldId) });
    },
  });
}

/**
 * Hook to analyze drainage for a field
 * خطاف لتحليل الصرف للحقل
 *
 * Triggers server-side drainage analysis using terrain data.
 *
 * @returns Mutation result with drainage analysis data
 */
export function useAnalyzeDrainage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => terrainApi.analyzeDrainage(fieldId),
    onSuccess: (_result: DrainageAnalysis, fieldId) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.drainage(fieldId) });
    },
  });
}

/**
 * Hook to analyze watershed for a field
 * خطاف لتحليل مستجمعات المياه للحقل
 *
 * Triggers server-side watershed delineation.
 *
 * @returns Mutation result with watershed analysis data
 */
export function useAnalyzeWatershed() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => terrainApi.analyzeWatershed(fieldId),
    onSuccess: (_result: WatershedAnalysis, fieldId) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.watershed(fieldId) });
    },
  });
}

/**
 * Hook to analyze flow accumulation for a field
 * خطاف لتحليل تراكم التدفق للحقل
 *
 * Triggers server-side flow accumulation analysis.
 *
 * @returns Mutation result with flow analysis data
 */
export function useAnalyzeFlow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => terrainApi.analyzeFlow(fieldId),
    onSuccess: (_result: FlowAnalysis, fieldId) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.flow(fieldId) });
    },
  });
}

/**
 * Hook to optimize field leveling
 * خطاف لتحسين تسوية الحقل
 *
 * Triggers server-side leveling optimization with optional target slope.
 *
 * @returns Mutation result with leveling plan data
 */
export function useOptimizeLeveling() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, targetSlope }: { fieldId: string; targetSlope?: number }) =>
      terrainApi.optimizeLeveling(fieldId, targetSlope),
    onSuccess: (_result: LevelingPlan, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.leveling(fieldId) });
      queryClient.invalidateQueries({ queryKey: terrainKeys.cutFill(fieldId) });
      queryClient.invalidateQueries({ queryKey: terrainKeys.cost(fieldId) });
    },
  });
}

/**
 * Hook to calculate cut/fill volumes for a field
 * خطاف لحساب أحجام القطع والردم للحقل
 *
 * Triggers server-side cut/fill calculation with optional target elevation.
 *
 * @returns Mutation result with cut/fill calculation data
 */
export function useCalculateCutFill() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ fieldId, targetElevation }: { fieldId: string; targetElevation?: number }) =>
      terrainApi.calculateCutFill(fieldId, targetElevation),
    onSuccess: (_result: CutFillResult, { fieldId }) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.cutFill(fieldId) });
      queryClient.invalidateQueries({ queryKey: terrainKeys.cost(fieldId) });
    },
  });
}

/**
 * Hook to estimate leveling cost for a field
 * خطاف لتقدير تكلفة التسوية للحقل
 *
 * Triggers server-side cost estimation based on cut/fill volumes.
 *
 * @returns Mutation result with leveling cost estimate
 */
export function useEstimateLevelingCost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (fieldId: string) => terrainApi.estimateLevelingCost(fieldId),
    onSuccess: (_result: LevelingCost, fieldId) => {
      queryClient.invalidateQueries({ queryKey: terrainKeys.cost(fieldId) });
    },
  });
}
