/**
 * Vision Feature - React Hooks
 * خطافات React لميزة الرؤية الحاسوبية
 *
 * React Query hooks for pest/disease/weed detection, plant counting,
 * ripeness classification, leaf segmentation, and model management.
 * خطافات لكشف الآفات/الأمراض/الأعشاب، عد النباتات،
 * تصنيف النضج، تجزئة الأوراق، وإدارة النماذج.
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { visionApi } from '../api';
import type { PestDetection, DiseaseDetection, WeedDetection, ModelInfo } from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys - مفاتيح الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

export const visionKeys = {
  all: ['vision'] as const,
  models: () => [...visionKeys.all, 'models'] as const,
  modelInfo: (variant: string) => [...visionKeys.all, 'modelInfo', variant] as const,
  detections: () => [...visionKeys.all, 'detections'] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks - خطافات الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch available vision model versions
 * خطاف لجلب إصدارات نماذج الرؤية المتاحة
 *
 * Retrieves all registered YOLO26 model variants and their metadata.
 *
 * @returns Query result with model info list
 */
export function useVisionModels() {
  return useQuery<ModelInfo[]>({
    queryKey: visionKeys.models(),
    queryFn: () => visionApi.getModels(),
    staleTime: 1000 * 60 * 30, // 30 minutes - models change infrequently
  });
}

/**
 * Hook to fetch info for a specific model variant
 * خطاف لجلب معلومات إصدار نموذج محدد
 *
 * Retrieves detailed info about a specific model variant (n/s/m/l/x).
 *
 * @param variant - Model variant identifier (n, s, m, l, x)
 * @returns Query result with model variant details
 */
export function useVisionModelInfo(variant: string) {
  return useQuery<ModelInfo>({
    queryKey: visionKeys.modelInfo(variant),
    queryFn: () => visionApi.getModelInfo(variant),
    enabled: !!variant,
    staleTime: 1000 * 60 * 30,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to detect pests in an image
 * خطاف لكشف الآفات في صورة
 *
 * Submits an image for YOLO26-based pest detection with optional confidence threshold.
 *
 * @returns Mutation result with pest detection data
 */
export function useDetectPest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ image, confidence }: { image: File; confidence?: number }) =>
      visionApi.detectPest(image, confidence),
    onSuccess: (_result: PestDetection) => {
      queryClient.invalidateQueries({ queryKey: visionKeys.detections() });
    },
  });
}

/**
 * Hook to detect diseases in an image
 * خطاف لكشف الأمراض في صورة
 *
 * Submits an image for YOLO26-based disease detection with optional confidence threshold.
 *
 * @returns Mutation result with disease detection data
 */
export function useDetectDisease() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ image, confidence }: { image: File; confidence?: number }) =>
      visionApi.detectDisease(image, confidence),
    onSuccess: (_result: DiseaseDetection) => {
      queryClient.invalidateQueries({ queryKey: visionKeys.detections() });
    },
  });
}

/**
 * Hook to detect weeds in an image
 * خطاف لكشف الأعشاب الضارة في صورة
 *
 * Submits an image for YOLO26-based weed detection with optional confidence threshold.
 *
 * @returns Mutation result with weed detection data
 */
export function useDetectWeed() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ image, confidence }: { image: File; confidence?: number }) =>
      visionApi.detectWeed(image, confidence),
    onSuccess: (_result: WeedDetection) => {
      queryClient.invalidateQueries({ queryKey: visionKeys.detections() });
    },
  });
}

/**
 * Hook to count plants in an image
 * خطاف لعد النباتات في صورة
 *
 * Submits an image for grid-based plant counting with density mapping.
 *
 * @returns Mutation result with plant count data
 */
export function useCountPlants() {
  return useMutation({
    mutationFn: (image: File) => visionApi.countPlants(image),
  });
}

/**
 * Hook to classify fruit/crop ripeness
 * خطاف لتصنيف نضج الثمار/المحصول
 *
 * Submits an image for 5-stage ripeness classification.
 *
 * @returns Mutation result with ripeness classification
 */
export function useClassifyRipeness() {
  return useMutation({
    mutationFn: (image: File) => visionApi.classifyRipeness(image),
  });
}

/**
 * Hook to perform leaf segmentation
 * خطاف لتجزئة الأوراق
 *
 * Submits an image for instance segmentation and LAI calculation.
 *
 * @returns Mutation result with leaf segmentation data
 */
export function useSegmentLeaf() {
  return useMutation({
    mutationFn: (image: File) => visionApi.segmentLeaf(image),
  });
}

/**
 * Hook to batch detect pests in multiple images
 * خطاف لكشف الآفات في صور متعددة
 *
 * Submits multiple images for batch pest detection processing.
 *
 * @returns Mutation result with batch pest detection results
 */
export function useBatchDetectPest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (images: File[]) => visionApi.batchDetectPest(images),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: visionKeys.detections() });
    },
  });
}

/**
 * Hook to batch detect diseases in multiple images
 * خطاف لكشف الأمراض في صور متعددة
 *
 * Submits multiple images for batch disease detection processing.
 *
 * @returns Mutation result with batch disease detection results
 */
export function useBatchDetectDisease() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (images: File[]) => visionApi.batchDetectDisease(images),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: visionKeys.detections() });
    },
  });
}

/**
 * Hook to warmup/preload vision models
 * خطاف لتحميل نماذج الرؤية مسبقاً
 *
 * Preloads specified model variants into GPU memory for faster inference.
 *
 * @returns Mutation result with warmup status
 */
export function useWarmupModels() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (variants?: string[]) => visionApi.warmupModels(variants),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: visionKeys.models() });
    },
  });
}
