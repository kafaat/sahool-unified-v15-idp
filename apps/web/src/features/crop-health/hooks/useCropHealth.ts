/**
 * Crop Health Feature - React Hooks
 * خطافات React لميزة صحة المحصول
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { HealthRecord, DiagnosisRequest, HealthFilters } from "../types";
import { cropHealthApi } from "../api";

// Query Keys
const HEALTH_KEYS = {
  all: ["crop-health"] as const,
  summary: (filters?: HealthFilters) =>
    [...HEALTH_KEYS.all, "summary", filters] as const,
  records: (filters?: HealthFilters) =>
    [...HEALTH_KEYS.all, "records", filters] as const,
  record: (id: string) => [...HEALTH_KEYS.all, "record", id] as const,
  diagnoses: () => [...HEALTH_KEYS.all, "diagnoses"] as const,
  diagnosis: (id: string) => [...HEALTH_KEYS.all, "diagnosis", id] as const,
  result: (id: string) => [...HEALTH_KEYS.all, "result", id] as const,
  diseases: () => [...HEALTH_KEYS.all, "diseases"] as const,
  alerts: () => [...HEALTH_KEYS.all, "alerts"] as const,
  consultations: () => [...HEALTH_KEYS.all, "consultations"] as const,
};

/**
 * Hook to fetch health summary
 */
export function useHealthSummary(filters?: HealthFilters) {
  return useQuery({
    queryKey: HEALTH_KEYS.summary(filters),
    queryFn: () => cropHealthApi.getHealthSummary(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch health records
 */
export function useHealthRecords(filters?: HealthFilters) {
  return useQuery({
    queryKey: HEALTH_KEYS.records(filters),
    queryFn: () => cropHealthApi.getHealthRecords(filters),
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to fetch a single health record
 */
export function useHealthRecord(id: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.record(id),
    queryFn: () => cropHealthApi.getHealthRecord(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a health record
 */
export function useCreateHealthRecord() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<HealthRecord>) =>
      cropHealthApi.createHealthRecord(data),
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
    mutationFn: ({ id, data }: { id: string; data: Partial<HealthRecord> }) =>
      cropHealthApi.updateHealthRecord(id, data),
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
    queryFn: () => cropHealthApi.getDiagnosisRequests(),
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Hook to fetch a diagnosis request
 */
export function useDiagnosisRequest(id: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.diagnosis(id),
    queryFn: () => cropHealthApi.getDiagnosisRequest(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a diagnosis request
 */
export function useCreateDiagnosis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<DiagnosisRequest>) =>
      cropHealthApi.submitDiagnosis(data),
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
    mutationFn: (files: File[]) => cropHealthApi.uploadDiagnosisImages(files),
  });
}

/**
 * Hook to fetch diagnosis result
 */
export function useDiagnosisResult(requestId: string) {
  return useQuery({
    queryKey: HEALTH_KEYS.result(requestId),
    queryFn: () => cropHealthApi.getDiagnosisResult(requestId),
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
    queryFn: () => cropHealthApi.getDiseases(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Hook to fetch disease alerts
 */
export function useDiseaseAlerts() {
  return useQuery({
    queryKey: HEALTH_KEYS.alerts(),
    queryFn: () => cropHealthApi.getDiseaseAlerts(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to dismiss an alert
 */
export function useDismissAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => cropHealthApi.dismissAlert(alertId),
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
    mutationFn: (data: {
      diagnosisId: string;
      question?: string;
      questionAr?: string;
    }) => cropHealthApi.requestConsultation(data),
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
    queryFn: () => cropHealthApi.getConsultations(),
    staleTime: 2 * 60 * 1000,
  });
}
