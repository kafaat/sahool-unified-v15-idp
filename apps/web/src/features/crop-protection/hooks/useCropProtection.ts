/**
 * Crop Protection Feature - React Hooks
 * خطافات React لميزة حماية المحاصيل
 */

'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
import { cropProtectionApi, type PestRecord, type SprayWindow, type PestIdentifyPayload } from '../api';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const cropProtectionKeys = {
  all: ['crop-protection'] as const,
  pests: (fieldId?: string) => [...cropProtectionKeys.all, 'pests', fieldId] as const,
  sprayWindows: (fieldId?: string) => [...cropProtectionKeys.all, 'spray-windows', fieldId] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch pest detection records
 * خطاف لجلب سجلات اكتشاف الآفات
 */
export function usePestRecords(fieldId?: string) {
  return useQuery<PestRecord[]>({
    queryKey: cropProtectionKeys.pests(fieldId),
    queryFn: () => cropProtectionApi.getPestRecords(fieldId),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch optimal spray windows
 * خطاف لجلب نوافذ الرش المثلى
 */
export function useSprayWindows(fieldId?: string) {
  return useQuery<SprayWindow[]>({
    queryKey: cropProtectionKeys.sprayWindows(fieldId),
    queryFn: () => cropProtectionApi.getSprayWindows(fieldId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to identify pest from image
 * خطاف لتحديد الآفة من الصورة
 */
export function useIdentifyPest() {
  return useMutation({
    mutationFn: (payload: PestIdentifyPayload) => cropProtectionApi.identifyPest(payload),
  });
}
