/**
 * Crop Insurance Feature - React Hooks
 * خطافات React لميزة التأمين على المحاصيل
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cropInsuranceApi } from '../api';
import type { PolicyFilters, ClaimFilters, PolicyFormData, ClaimFormData } from '../types';

export const insuranceKeys = {
  all: ['crop-insurance'] as const,
  policies: () => [...insuranceKeys.all, 'policies'] as const,
  policyList: (filters?: PolicyFilters) => [...insuranceKeys.policies(), filters] as const,
  policyDetail: (id: string) => [...insuranceKeys.policies(), 'detail', id] as const,
  providers: () => [...insuranceKeys.all, 'providers'] as const,
  claims: () => [...insuranceKeys.all, 'claims'] as const,
  claimList: (filters?: ClaimFilters) => [...insuranceKeys.claims(), filters] as const,
  claimDetail: (id: string) => [...insuranceKeys.claims(), 'detail', id] as const,
  riskProfile: (fieldId: string) => [...insuranceKeys.all, 'risk-profile', fieldId] as const,
  stats: () => [...insuranceKeys.all, 'stats'] as const,
};

export function usePolicies(filters?: PolicyFilters) {
  return useQuery({
    queryKey: insuranceKeys.policyList(filters),
    queryFn: () => cropInsuranceApi.getPolicies(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function usePolicy(id: string) {
  return useQuery({
    queryKey: insuranceKeys.policyDetail(id),
    queryFn: () => cropInsuranceApi.getPolicy(id),
    enabled: !!id,
  });
}

export function useCreatePolicy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: PolicyFormData) => cropInsuranceApi.createPolicy(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: insuranceKeys.policies() });
      qc.invalidateQueries({ queryKey: insuranceKeys.stats() });
    },
  });
}

export function useUpdatePolicy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<PolicyFormData> }) =>
      cropInsuranceApi.updatePolicy(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: insuranceKeys.policies() });
      qc.invalidateQueries({ queryKey: insuranceKeys.policyDetail(id) });
      qc.invalidateQueries({ queryKey: insuranceKeys.stats() });
    },
  });
}

export function useProviders() {
  return useQuery({
    queryKey: insuranceKeys.providers(),
    queryFn: () => cropInsuranceApi.getProviders(),
    staleTime: 1000 * 60 * 10,
  });
}

export function useClaims(filters?: ClaimFilters) {
  return useQuery({
    queryKey: insuranceKeys.claimList(filters),
    queryFn: () => cropInsuranceApi.getClaims(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useClaim(id: string) {
  return useQuery({
    queryKey: insuranceKeys.claimDetail(id),
    queryFn: () => cropInsuranceApi.getClaim(id),
    enabled: !!id,
  });
}

export function useSubmitClaim() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ClaimFormData) => cropInsuranceApi.submitClaim(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: insuranceKeys.claims() });
      qc.invalidateQueries({ queryKey: insuranceKeys.stats() });
    },
  });
}

export function useUploadEvidence() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ claimId, files }: { claimId: string; files: File[] }) =>
      cropInsuranceApi.uploadEvidence(claimId, files),
    onSuccess: (_, { claimId }) => {
      qc.invalidateQueries({ queryKey: insuranceKeys.claimDetail(claimId) });
    },
  });
}

export function useRiskProfile(fieldId: string) {
  return useQuery({
    queryKey: insuranceKeys.riskProfile(fieldId),
    queryFn: () => cropInsuranceApi.getRiskProfile(fieldId),
    enabled: !!fieldId,
    staleTime: 1000 * 60 * 10,
  });
}

export function useCalculatePremium() {
  return useMutation({
    mutationFn: (policyData: PolicyFormData) =>
      cropInsuranceApi.calculatePremium(policyData),
  });
}

export function useInsuranceStats() {
  return useQuery({
    queryKey: insuranceKeys.stats(),
    queryFn: () => cropInsuranceApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}
