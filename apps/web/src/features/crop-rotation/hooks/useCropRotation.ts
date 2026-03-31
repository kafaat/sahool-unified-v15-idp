/**
 * Crop Rotation Feature - React Hooks
 * خطافات React لميزة الدورة الزراعية
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cropRotationApi } from '../api';
import type { CropRotationFilters, CropType, RotationPlanFormData } from '../types';

export const cropRotationKeys = {
  all: ['crop-rotation'] as const,
  plans: () => [...cropRotationKeys.all, 'plans'] as const,
  planList: (filters?: CropRotationFilters) => [...cropRotationKeys.plans(), filters] as const,
  planDetail: (id: string) => [...cropRotationKeys.plans(), 'detail', id] as const,
  recommendations: (fieldId: string, currentCrop?: CropType) =>
    [...cropRotationKeys.all, 'recommendations', fieldId, currentCrop] as const,
  multiYearPlan: (fieldId: string, years: number) =>
    [...cropRotationKeys.all, 'multi-year-plan', fieldId, years] as const,
  fieldHistory: (fieldId: string) =>
    [...cropRotationKeys.all, 'history', fieldId] as const,
  pestBreak: (fieldId: string, crop: CropType) =>
    [...cropRotationKeys.all, 'pest-break', fieldId, crop] as const,
  soilHealth: (fieldId: string) =>
    [...cropRotationKeys.all, 'soil-health', fieldId] as const,
  crops: (cropType?: CropType) =>
    [...cropRotationKeys.all, 'crops', cropType] as const,
  stats: () => [...cropRotationKeys.all, 'stats'] as const,
};

// ── Plan hooks ───────────────────────────────────────────────────

export function useRotationPlans(filters?: CropRotationFilters) {
  return useQuery({
    queryKey: cropRotationKeys.planList(filters),
    queryFn: () => cropRotationApi.getPlans(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useRotationPlan(id: string) {
  return useQuery({
    queryKey: cropRotationKeys.planDetail(id),
    queryFn: () => cropRotationApi.getPlan(id),
    enabled: !!id,
  });
}

export function useCreateRotationPlan() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: RotationPlanFormData) => cropRotationApi.createPlan(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: cropRotationKeys.plans() });
      qc.invalidateQueries({ queryKey: cropRotationKeys.stats() });
    },
  });
}

export function useUpdateRotationPlan() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<RotationPlanFormData> }) =>
      cropRotationApi.updatePlan(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: cropRotationKeys.plans() });
      qc.invalidateQueries({ queryKey: cropRotationKeys.planDetail(id) });
    },
  });
}

export function useDeleteRotationPlan() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cropRotationApi.deletePlan(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: cropRotationKeys.plans() });
      qc.removeQueries({ queryKey: cropRotationKeys.planDetail(id) });
      qc.invalidateQueries({ queryKey: cropRotationKeys.stats() });
    },
  });
}

// ── Recommendation hooks ─────────────────────────────────────────

export function useRotationRecommendation(fieldId: string, currentCrop?: CropType) {
  return useQuery({
    queryKey: cropRotationKeys.recommendations(fieldId, currentCrop),
    queryFn: () => cropRotationApi.getRecommendation(fieldId, currentCrop),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 10,
  });
}

export function useMultiYearPlan(fieldId: string, durationYears: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => cropRotationApi.getMultiYearPlan(fieldId, durationYears),
    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: cropRotationKeys.multiYearPlan(fieldId, durationYears),
      });
    },
  });
}

// ── History & Analysis hooks ─────────────────────────────────────

export function useFieldRotationHistory(fieldId: string) {
  return useQuery({
    queryKey: cropRotationKeys.fieldHistory(fieldId),
    queryFn: () => cropRotationApi.getFieldHistory(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 5,
  });
}

export function usePestBreakRecommendation(fieldId: string, currentCrop: CropType) {
  return useQuery({
    queryKey: cropRotationKeys.pestBreak(fieldId, currentCrop),
    queryFn: () => cropRotationApi.getPestBreakRecommendation(fieldId, currentCrop),
    enabled: !!fieldId && !!currentCrop,
    staleTime: 1000 * 60 * 10,
  });
}

export function useSoilHealthReport(fieldId: string) {
  return useQuery({
    queryKey: cropRotationKeys.soilHealth(fieldId),
    queryFn: () => cropRotationApi.getSoilHealthReport(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 5,
  });
}

// ── Reference Data hooks ─────────────────────────────────────────

export function useCropCharacteristics(cropType?: CropType) {
  return useQuery({
    queryKey: cropRotationKeys.crops(cropType),
    queryFn: () => cropRotationApi.getCropCharacteristics(cropType),
    staleTime: 1000 * 60 * 30,
  });
}

// ── Stats hooks ──────────────────────────────────────────────────

export function useCropRotationStats() {
  return useQuery({
    queryKey: cropRotationKeys.stats(),
    queryFn: () => cropRotationApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}
