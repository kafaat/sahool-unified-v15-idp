/**
 * Harvest Quality Feature - React Hooks
 * خطافات React لميزة جودة الحصاد
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { harvestQualityApi } from '../api';
import type { HarvestQualityFilters, QualityTestFormData } from '../types';

export const harvestQualityKeys = {
  all: ['harvest-quality'] as const,
  tests: () => [...harvestQualityKeys.all, 'tests'] as const,
  testList: (filters?: HarvestQualityFilters) => [...harvestQualityKeys.tests(), filters] as const,
  testDetail: (id: string) => [...harvestQualityKeys.tests(), 'detail', id] as const,
  standards: (cropType?: string) => [...harvestQualityKeys.all, 'standards', cropType] as const,
  buyerMatches: (batchId: string) => [...harvestQualityKeys.all, 'buyers', batchId] as const,
  priceMatrix: (cropType: string) => [...harvestQualityKeys.all, 'price-matrix', cropType] as const,
  trends: (fieldId: string) => [...harvestQualityKeys.all, 'trends', fieldId] as const,
  stats: () => [...harvestQualityKeys.all, 'stats'] as const,
};

export function useHarvestQualityTests(filters?: HarvestQualityFilters) {
  return useQuery({
    queryKey: harvestQualityKeys.testList(filters),
    queryFn: () => harvestQualityApi.getTestRecords(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useHarvestQualityTest(id: string) {
  return useQuery({
    queryKey: harvestQualityKeys.testDetail(id),
    queryFn: () => harvestQualityApi.getTestRecord(id),
    enabled: !!id,
  });
}

export function useCreateQualityTest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: QualityTestFormData) => harvestQualityApi.createTestRecord(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: harvestQualityKeys.tests() });
      qc.invalidateQueries({ queryKey: harvestQualityKeys.stats() });
    },
  });
}

export function useQualityStandards(cropType?: string) {
  return useQuery({
    queryKey: harvestQualityKeys.standards(cropType),
    queryFn: () => harvestQualityApi.getStandards(cropType),
    staleTime: 1000 * 60 * 30,
  });
}

export function useBuyerMatches(batchId: string) {
  return useQuery({
    queryKey: harvestQualityKeys.buyerMatches(batchId),
    queryFn: () => harvestQualityApi.findBuyerMatches(batchId),
    enabled: !!batchId,
  });
}

export function usePriceMatrix(cropType: string) {
  return useQuery({
    queryKey: harvestQualityKeys.priceMatrix(cropType),
    queryFn: () => harvestQualityApi.getPriceMatrix(cropType),
    enabled: !!cropType,
    staleTime: 1000 * 60 * 15,
  });
}

export function useCalculatePrice() {
  return useMutation({
    mutationFn: (batchId: string) => harvestQualityApi.calculatePrice(batchId),
  });
}

export function useQualityTrends(fieldId: string, periodDays?: number) {
  return useQuery({
    queryKey: harvestQualityKeys.trends(fieldId),
    queryFn: () => harvestQualityApi.getQualityTrends(fieldId, periodDays),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 10,
  });
}

export function useHarvestQualityStats() {
  return useQuery({
    queryKey: harvestQualityKeys.stats(),
    queryFn: () => harvestQualityApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}
