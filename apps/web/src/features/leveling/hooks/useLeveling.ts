/**
 * Leveling Optimizer Feature - React Hooks
 * خطافات React لميزة تحسين التسوية
 *
 * React Query hooks for field leveling analysis, plan retrieval,
 * cost estimation, equipment recommendations, and simulation.
 * خطافات لتحليل تسوية الحقل، استرجاع الخطة، تقدير التكلفة،
 * توصيات المعدات، والمحاكاة.
 */

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { levelingApi } from '../api';
import type {
  LevelingAnalysis,
  LevelingAnalysisRequest,
  CostEstimationParams,
  EquipmentRecommendationParams,
  LevelingSimulation,
  LevelingSimulationRequest,
} from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys - مفاتيح الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

export const levelingKeys = {
  all: ['leveling'] as const,
  analysis: (fieldId: string) => [...levelingKeys.all, 'analysis', fieldId] as const,
  plan: (fieldId: string) => [...levelingKeys.all, 'plan', fieldId] as const,
  cost: (fieldId: string) => [...levelingKeys.all, 'cost', fieldId] as const,
  equipment: (fieldId: string) => [...levelingKeys.all, 'equipment', fieldId] as const,
  simulation: (fieldId: string) => [...levelingKeys.all, 'simulation', fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to analyze a field for leveling requirements
 * خطاف لتحليل الحقل لمتطلبات التسوية
 *
 * Triggers server-side leveling analysis with elevation points
 * and returns an optimal leveling plan with cost estimates.
 *
 * @returns Mutation result with leveling analysis data
 */
export function useAnalyzeFieldLeveling() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: LevelingAnalysisRequest) =>
      levelingApi.analyzeFieldLeveling(request),
    onSuccess: (_result: LevelingAnalysis, request) => {
      queryClient.invalidateQueries({ queryKey: levelingKeys.analysis(request.fieldId) });
      queryClient.invalidateQueries({ queryKey: levelingKeys.plan(request.fieldId) });
      queryClient.invalidateQueries({ queryKey: levelingKeys.cost(request.fieldId) });
      queryClient.invalidateQueries({ queryKey: levelingKeys.equipment(request.fieldId) });
    },
  });
}

/**
 * Hook to get the optimal leveling plan for a field
 * خطاف للحصول على خطة التسوية المثلى للحقل
 *
 * Retrieves a stored leveling plan from the server.
 *
 * @param fieldId - The field ID to retrieve the plan for
 * @returns Query result with leveling plan data
 */
export function useGetLevelingPlan(fieldId: string | undefined) {
  return useQuery({
    queryKey: levelingKeys.plan(fieldId ?? ''),
    queryFn: () => levelingApi.getLevelingPlan(fieldId!),
    enabled: !!fieldId,
  });
}

/**
 * Hook to get cost estimation for leveling operation
 * خطاف للحصول على تقدير التكلفة لعملية التسوية
 *
 * Fetches cost estimation based on cut/fill volumes.
 *
 * @param params - Cost estimation parameters (pass undefined to disable)
 * @returns Query result with cost estimation data
 */
export function useGetCostEstimation(params: CostEstimationParams | undefined) {
  return useQuery({
    queryKey: levelingKeys.cost(params?.fieldId ?? ''),
    queryFn: () => levelingApi.getCostEstimation(params!),
    enabled: !!params?.fieldId,
  });
}

/**
 * Hook to get equipment recommendations for leveling operation
 * خطاف للحصول على توصيات المعدات لعملية التسوية
 *
 * Returns recommended equipment based on earthwork volume and haul distance.
 *
 * @param params - Equipment recommendation parameters (pass undefined to disable)
 * @returns Query result with equipment recommendation list
 */
export function useGetEquipmentRecommendations(params: EquipmentRecommendationParams | undefined) {
  return useQuery({
    queryKey: levelingKeys.equipment(params?.fieldId ?? ''),
    queryFn: () => levelingApi.getEquipmentRecommendations(params!),
    enabled: !!params?.fieldId,
  });
}

/**
 * Hook to simulate a leveling scenario
 * خطاف لمحاكاة سيناريو التسوية
 *
 * Triggers server-side simulation with target grades and elevation,
 * returning predicted cut/fill volumes and uniformity improvement.
 *
 * @returns Mutation result with simulation data
 */
export function useSimulateLeveling() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: LevelingSimulationRequest) =>
      levelingApi.simulateLeveling(request),
    onSuccess: (_result: LevelingSimulation, request) => {
      queryClient.invalidateQueries({ queryKey: levelingKeys.simulation(request.fieldId) });
      queryClient.invalidateQueries({ queryKey: levelingKeys.cost(request.fieldId) });
    },
  });
}
