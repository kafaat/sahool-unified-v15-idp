/**
 * Crop Planning Feature - React Hooks
 * خطافات React لميزة تخطيط المحاصيل
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  cropPlanningApi,
  type CropPlan,
  type CropRecommendation,
  type CreateCropPlanPayload,
} from '../api';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const cropPlanningKeys = {
  all: ['crop-planning'] as const,
  plans: (fieldId?: string) => [...cropPlanningKeys.all, 'plans', fieldId] as const,
  recommendations: (fieldId?: string) => [...cropPlanningKeys.all, 'recommendations', fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch crop plans
 * خطاف لجلب خطط المحاصيل
 */
export function useCropPlans(fieldId?: string) {
  return useQuery<CropPlan[]>({
    queryKey: cropPlanningKeys.plans(fieldId),
    queryFn: () => cropPlanningApi.getPlans(fieldId),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch crop recommendations for a field
 * خطاف لجلب توصيات المحاصيل لحقل معين
 */
export function useCropRecommendations(fieldId?: string) {
  return useQuery<CropRecommendation[]>({
    queryKey: cropPlanningKeys.recommendations(fieldId),
    queryFn: () => cropPlanningApi.getRecommendations(fieldId),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to create a new crop plan
 * خطاف لإنشاء خطة محصول جديدة
 */
export function useCreateCropPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateCropPlanPayload) => cropPlanningApi.createPlan(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cropPlanningKeys.all });
    },
  });
}
