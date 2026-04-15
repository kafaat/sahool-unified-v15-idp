/**
 * Documents Feature - React Hooks
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi } from '../api';
import type { DocumentFilters } from '../types';

export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (filters?: DocumentFilters) => [...documentKeys.lists(), filters] as const,
  detail: (id: string) => [...documentKeys.all, 'detail', id] as const,
  stats: () => [...documentKeys.all, 'stats'] as const,
};

export function useDocuments(filters?: DocumentFilters) {
  return useQuery({
    queryKey: documentKeys.list(filters),
    queryFn: () => documentsApi.getDocuments(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentsApi.getDocumentById(id),
    enabled: !!id,
  });
}

export function useDocumentStats() {
  return useQuery({
    queryKey: documentKeys.stats(),
    queryFn: () => documentsApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => documentsApi.uploadDocument(formData),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
      qc.invalidateQueries({ queryKey: documentKeys.stats() });
    },
  });
}

export function useDeleteDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.deleteDocument(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: documentKeys.lists() });
      qc.removeQueries({ queryKey: documentKeys.detail(id) });
      qc.invalidateQueries({ queryKey: documentKeys.stats() });
    },
  });
}
