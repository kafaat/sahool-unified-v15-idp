/**
 * Soil Analysis Feature - React Hooks
 * خطافات React لميزة تحليل التربة
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { soilApi } from "../api";
import type { SoilTest, SoilFilters } from "../types";

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const soilKeys = {
  all: ["soil-analysis"] as const,
  lists: () => [...soilKeys.all, "list"] as const,
  list: (filters?: SoilFilters) => [...soilKeys.lists(), filters] as const,
  detail: (id: string) => [...soilKeys.all, "detail", id] as const,
  recommendations: (fieldId?: string) =>
    [...soilKeys.all, "recommendations", fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks (Read Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch soil tests with optional filters
 * خطاف لجلب اختبارات التربة مع فلاتر اختيارية
 */
export function useSoilTests(filters?: SoilFilters) {
  return useQuery({
    queryKey: soilKeys.list(filters),
    queryFn: () => soilApi.getTests(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch a single soil test by ID
 * خطاف لجلب اختبار تربة واحد بواسطة المعرف
 */
export function useSoilTest(id: string) {
  return useQuery({
    queryKey: soilKeys.detail(id),
    queryFn: () => soilApi.getTestById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch soil recommendations for a field
 * خطاف لجلب توصيات التربة لحقل معين
 */
export function useSoilRecommendations(fieldId?: string) {
  return useQuery({
    queryKey: soilKeys.recommendations(fieldId),
    queryFn: () => soilApi.getRecommendations(fieldId),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks (Write Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to create a new soil test
 * خطاف لإنشاء اختبار تربة جديد
 */
export function useCreateSoilTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<SoilTest, "id">) => soilApi.createTest(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: soilKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: [...soilKeys.all, "recommendations"],
      });
    },
  });
}
