/**
 * Crop Health Feature - React Hooks
 * خطافات React لميزة صحة المحصول
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import type {
  HealthSummary,
  HealthRecord,
  DiagnosisRequest,
  DiagnosisResult,
  Disease,
  DiseaseAlert,
  HealthFilters,
  ExpertConsultation,
} from '../types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Query Keys
const HEALTH_KEYS = {
  all: ['crop-health'] as const,
  summary: (filters?: HealthFilters) => [...HEALTH_KEYS.all, 'summary', filters] as const,
  records: (filters?: HealthFilters) => [...HEALTH_KEYS.all, 'records', filters] as const,
  record: (id: string) => [...HEALTH_KEYS.all, 'record', id] as const,
  diagnoses: () => [...HEALTH_KEYS.all, 'diagnoses'] as const,
  diagnosis: (id: string) => [...HEALTH_KEYS.all, 'diagnosis', id] as const,
  result: (id: string) => [...HEALTH_KEYS.all, 'result', id] as const,
  diseases: () => [...HEALTH_KEYS.all, 'diseases'] as const,
  alerts: () => [...HEALTH_KEYS.all, 'alerts'] as const,
  consultations: () => [...HEALTH_KEYS.all, 'consultations'] as const,
};

/**
 * Hook to fetch health summary
 */
export function useHealthSummary(filters?: HealthFilters) {
  return useQuery({
    queryKey: HEALTH_KEYS.summary(filters),
    queryFn: async (): Promise<HealthSummary> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.status?.length) params.set('status', filters.status.join(','));
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);

      const response = await api.get(`/v1/crop-health/summary?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch health records
 */
export function useHealthRecords(filters?: HealthFilters) {
  return useQuery({
    queryKey: HEALTH_KEYS.records(filters),
    queryFn: async (): Promise<HealthRecord[]> => {
      const params = new URLSearchParams();
      if (filters?.fieldIds?.length) params.set('field_ids', filters.fieldIds.join(','));
      if (filters?.cropTypes?.length) params.set('crop_types', filters.cropTypes.join(','));
      if (filters?.status?.length) params.set('status', filters.status.join(','));
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);
      if (filters?.severity?.length) params.set('severity', filters.severity.join(','));

      const response = await api.get(`/v1/crop-health/records?${params.toString()}`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to fetch a single health record
 */
export function useHealthRecord(id: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.record(id),
    queryFn: async (): Promise<HealthRecord> => {
      const response = await api.get(`/v1/crop-health/records/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Hook to create a health record
 */
export function useCreateHealthRecord() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<HealthRecord>): Promise<HealthRecord> => {
      const response = await api.post('/v1/crop-health/records', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.all });
    },
  });
}

/**
 * Hook to update a health record
 */
export function useUpdateHealthRecord() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<HealthRecord> }): Promise<HealthRecord> => {
      const response = await api.put(`/v1/crop-health/records/${id}`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.record(id) });
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.records() });
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.summary() });
    },
  });
}

/**
 * Hook to fetch user's diagnosis requests
 */
export function useDiagnosisRequests() {
  return useQuery({
    queryKey: HEALTH_KEYS.diagnoses(),
    queryFn: async (): Promise<DiagnosisRequest[]> => {
      const response = await api.get('/v1/crop-health/diagnoses');
      return response.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to fetch a diagnosis request
 */
export function useDiagnosisRequest(id: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.diagnosis(id),
    queryFn: async (): Promise<DiagnosisRequest> => {
      const response = await api.get(`/v1/crop-health/diagnoses/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Hook to create a diagnosis request
 */
export function useCreateDiagnosis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<DiagnosisRequest>): Promise<DiagnosisRequest> => {
      const response = await api.post('/v1/crop-health/diagnoses', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.diagnoses() });
    },
  });
}

/**
 * Hook to upload images for diagnosis
 */
export function useUploadDiagnosisImages() {
  return useMutation({
    mutationFn: async (files: File[]): Promise<string[]> => {
      const formData = new FormData();
      files.forEach((file) => formData.append('images', file));

      const response = await api.post('/v1/crop-health/diagnoses/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data.urls;
    },
  });
}

/**
 * Hook to fetch diagnosis result
 */
export function useDiagnosisResult(requestId: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.result(requestId),
    queryFn: async (): Promise<DiagnosisResult> => {
      const response = await api.get(`/v1/crop-health/diagnoses/${requestId}/result`);
      return response.data;
    },
    enabled: !!requestId,
    refetchInterval: (query) => {
      // Poll every 5 seconds if we don't have a result yet (no analyzedAt means still processing)
      const data = query.state.data;
      // If no data or no analyzedAt, keep polling
      return !data || !data.analyzedAt ? 5000 : false;
    },
  });
}

/**
 * Hook to fetch disease database
 */
export function useDiseases() {
  return useQuery({
    queryKey: HEALTH_KEYS.diseases(),
    queryFn: async (): Promise<Disease[]> => {
      const response = await api.get('/v1/crop-health/diseases');
      return response.data;
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Hook to fetch disease alerts
 */
export function useDiseaseAlerts() {
  return useQuery({
    queryKey: HEALTH_KEYS.alerts(),
    queryFn: async (): Promise<DiseaseAlert[]> => {
      const response = await api.get('/v1/crop-health/alerts');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to dismiss an alert
 */
export function useDismissAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (alertId: string): Promise<void> => {
      await api.post(`/v1/crop-health/alerts/${alertId}/dismiss`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.alerts() });
    },
  });
}

/**
 * Hook to request expert consultation
 */
export function useRequestConsultation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      diagnosisId: string;
      question?: string;
      questionAr?: string;
    }): Promise<ExpertConsultation> => {
      const response = await api.post('/v1/crop-health/consultations', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: HEALTH_KEYS.consultations() });
    },
  });
}

/**
 * Hook to fetch user's consultations
 */
export function useConsultations() {
  return useQuery({
    queryKey: HEALTH_KEYS.consultations(),
    queryFn: async (): Promise<ExpertConsultation[]> => {
      const response = await api.get('/v1/crop-health/consultations');
      return response.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}
