/**
 * Compliance Feature - React Hooks
 * خطافات React لميزة الامتثال والجودة
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { complianceApi } from '../api';
import type { ComplianceFilters, ComplianceItem, AuditReport } from '../types';

export const complianceKeys = {
  all: ['compliance'] as const,
  lists: () => [...complianceKeys.all, 'list'] as const,
  list: (filters?: ComplianceFilters) => [...complianceKeys.lists(), filters] as const,
  detail: (id: string) => [...complianceKeys.all, 'detail', id] as const,
  stats: () => [...complianceKeys.all, 'stats'] as const,
  certifications: {
    all: ['certifications'] as const,
    lists: () => [...complianceKeys.certifications.all, 'list'] as const,
    detail: (id: string) => [...complianceKeys.certifications.all, 'detail', id] as const,
  },
  audits: {
    all: ['audits'] as const,
    lists: () => [...complianceKeys.audits.all, 'list'] as const,
  },
};

export function useCompliance(filters?: ComplianceFilters) {
  return useQuery({
    queryKey: complianceKeys.list(filters),
    queryFn: () => complianceApi.getCompliance(filters),
    staleTime: 1000 * 60 * 10,
  });
}

export function useComplianceDetails(id: string) {
  return useQuery({
    queryKey: complianceKeys.detail(id),
    queryFn: () => complianceApi.getComplianceById(id),
    enabled: !!id,
  });
}

export function useComplianceStats() {
  return useQuery({
    queryKey: complianceKeys.stats(),
    queryFn: () => complianceApi.getStats(),
    staleTime: 1000 * 60 * 10,
  });
}

export function useCertifications() {
  return useQuery({
    queryKey: complianceKeys.certifications.lists(),
    queryFn: () => complianceApi.getCertifications(),
    staleTime: 1000 * 60 * 30, // 30 minutes - certifications don't change often
  });
}

export function useCertificationDetails(id: string) {
  return useQuery({
    queryKey: complianceKeys.certifications.detail(id),
    queryFn: () => complianceApi.getCertificationById(id),
    enabled: !!id,
  });
}

export function useAuditReports() {
  return useQuery({
    queryKey: complianceKeys.audits.lists(),
    queryFn: () => complianceApi.getAuditReports(),
    staleTime: 1000 * 60 * 15,
  });
}

export function useUpdateCompliance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ComplianceItem> }) =>
      complianceApi.updateCompliance(id, data),
    onSuccess: (updatedItem) => {
      queryClient.invalidateQueries({ queryKey: complianceKeys.lists() });
      queryClient.setQueryData(complianceKeys.detail(updatedItem.id), updatedItem);
      queryClient.invalidateQueries({ queryKey: complianceKeys.stats() });
    },
  });
}

export function useCreateAuditReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<AuditReport>) => complianceApi.createAuditReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: complianceKeys.audits.lists() });
      queryClient.invalidateQueries({ queryKey: complianceKeys.lists() });
      queryClient.invalidateQueries({ queryKey: complianceKeys.stats() });
    },
  });
}
