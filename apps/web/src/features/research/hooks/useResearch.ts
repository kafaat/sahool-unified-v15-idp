/**
 * Research Feature - React Hooks
 * خطافات React لميزة الأبحاث والتجارب
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { researchApi } from '../api';
import type { ResearchFilters, ResearchFormData } from '../types';

export const researchKeys = {
  all: ['research'] as const,
  lists: () => [...researchKeys.all, 'list'] as const,
  list: (filters?: ResearchFilters) => [...researchKeys.lists(), filters] as const,
  detail: (id: string) => [...researchKeys.all, 'detail', id] as const,
  stats: () => [...researchKeys.all, 'stats'] as const,
  milestones: (trialId: string) => [...researchKeys.all, 'milestones', trialId] as const,
};

export function useResearchTrials(filters?: ResearchFilters) {
  return useQuery({
    queryKey: researchKeys.list(filters),
    queryFn: () => researchApi.getTrials(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useResearchTrialDetails(id: string) {
  return useQuery({
    queryKey: researchKeys.detail(id),
    queryFn: () => researchApi.getTrialById(id),
    enabled: !!id,
  });
}

export function useResearchStats() {
  return useQuery({
    queryKey: researchKeys.stats(),
    queryFn: () => researchApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useResearchMilestones(trialId: string) {
  return useQuery({
    queryKey: researchKeys.milestones(trialId),
    queryFn: () => researchApi.getMilestones(trialId),
    enabled: !!trialId,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreateResearchTrial() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ResearchFormData) => researchApi.createTrial(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: researchKeys.lists() });
      queryClient.invalidateQueries({ queryKey: researchKeys.stats() });
    },
  });
}

export function useUpdateResearchTrial() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ResearchFormData> }) =>
      researchApi.updateTrial(id, data),
    onSuccess: (updatedTrial) => {
      queryClient.invalidateQueries({ queryKey: researchKeys.lists() });
      queryClient.setQueryData(researchKeys.detail(updatedTrial.id), updatedTrial);
      queryClient.invalidateQueries({ queryKey: researchKeys.stats() });
    },
  });
}

export function useDeleteResearchTrial() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => researchApi.deleteTrial(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: researchKeys.lists() });
      queryClient.removeQueries({ queryKey: researchKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: researchKeys.stats() });
    },
  });
}

export function useUpdateResearchProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, progress }: { id: string; progress: number }) =>
      researchApi.updateProgress(id, progress),
    onSuccess: (updatedTrial) => {
      queryClient.invalidateQueries({ queryKey: researchKeys.lists() });
      queryClient.setQueryData(researchKeys.detail(updatedTrial.id), updatedTrial);
    },
  });
}
