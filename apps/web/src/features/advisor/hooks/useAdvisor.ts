/**
 * Advisor Feature - React Hooks
 * خطافات React لميزة المستشار الزراعي
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { advisorApi, type AdvisorQuery, type AdvisorFilters } from "../api";

// Query Keys
const ADVISOR_KEYS = {
  all: ["advisor"] as const,
  recommendations: (filters?: AdvisorFilters) =>
    [...ADVISOR_KEYS.all, "recommendations", filters] as const,
  recommendation: (id: string) =>
    [...ADVISOR_KEYS.all, "recommendation", id] as const,
  history: (limit?: number) => [...ADVISOR_KEYS.all, "history", limit] as const,
  stats: () => [...ADVISOR_KEYS.all, "stats"] as const,
};

/**
 * Hook to fetch recommendations
 */
export function useRecommendations(filters?: AdvisorFilters) {
  return useQuery({
    queryKey: ADVISOR_KEYS.recommendations(filters),
    queryFn: () => advisorApi.getRecommendations(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch a single recommendation
 */
export function useRecommendation(id: string) {
  return useQuery({
    queryKey: ADVISOR_KEYS.recommendation(id),
    queryFn: () => advisorApi.getRecommendation(id),
    enabled: !!id,
  });
}

/**
 * Hook to ask the AI advisor
 */
export function useAskAdvisor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (query: AdvisorQuery) => advisorApi.askAdvisor(query),
    onSuccess: () => {
      // Invalidate history and recommendations after asking
      queryClient.invalidateQueries({ queryKey: ADVISOR_KEYS.all });
    },
  });
}

/**
 * Hook to apply a recommendation
 */
export function useApplyRecommendation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      advisorApi.applyRecommendation(id, notes),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({
        queryKey: ADVISOR_KEYS.recommendation(id),
      });
      queryClient.invalidateQueries({
        queryKey: ADVISOR_KEYS.recommendations(),
      });
      queryClient.invalidateQueries({ queryKey: ADVISOR_KEYS.stats() });
    },
  });
}

/**
 * Hook to dismiss a recommendation
 */
export function useDismissRecommendation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      advisorApi.dismissRecommendation(id, reason),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({
        queryKey: ADVISOR_KEYS.recommendation(id),
      });
      queryClient.invalidateQueries({
        queryKey: ADVISOR_KEYS.recommendations(),
      });
      queryClient.invalidateQueries({ queryKey: ADVISOR_KEYS.stats() });
    },
  });
}

/**
 * Hook to complete an action item
 */
export function useCompleteAction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      recommendationId,
      actionId,
    }: {
      recommendationId: string;
      actionId: string;
    }) => advisorApi.completeAction(recommendationId, actionId),
    onSuccess: (_, { recommendationId }) => {
      queryClient.invalidateQueries({
        queryKey: ADVISOR_KEYS.recommendation(recommendationId),
      });
    },
  });
}

/**
 * Hook to fetch chat history
 */
export function useAdvisorHistory(limit?: number) {
  return useQuery({
    queryKey: ADVISOR_KEYS.history(limit),
    queryFn: () => advisorApi.getChatHistory(limit),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch advisor statistics
 */
export function useAdvisorStats() {
  return useQuery({
    queryKey: ADVISOR_KEYS.stats(),
    queryFn: () => advisorApi.getStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
