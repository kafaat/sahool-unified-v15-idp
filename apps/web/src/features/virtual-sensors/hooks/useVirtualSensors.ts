/**
 * Virtual Sensors Feature - React Hooks
 * خطافات React لميزة الحساسات الافتراضية
 *
 * React Query hooks for ET0/ETC calculation, crop Kc, soil moisture estimation,
 * and irrigation recommendations.
 * خطافات لحساب التبخر-نتح المرجعي والفعلي، معامل المحصول، تقدير رطوبة التربة،
 * وتوصيات الري.
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { virtualSensorsApi } from '../api';
import type {
  ET0Result,
  ETCResult,
  CropInfo,
  SoilInfo,
  SoilMoistureEstimate,
  IrrigationRecommendation,
} from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys - مفاتيح الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

export const virtualSensorKeys = {
  all: ['virtual-sensors'] as const,
  crops: () => [...virtualSensorKeys.all, 'crops'] as const,
  cropKc: (cropType: string) => [...virtualSensorKeys.all, 'cropKc', cropType] as const,
  soils: () => [...virtualSensorKeys.all, 'soils'] as const,
  irrigationMethods: () => [...virtualSensorKeys.all, 'irrigationMethods'] as const,
  et0: () => [...virtualSensorKeys.all, 'et0'] as const,
  etc: () => [...virtualSensorKeys.all, 'etc'] as const,
  soilMoisture: () => [...virtualSensorKeys.all, 'soilMoisture'] as const,
  irrigation: () => [...virtualSensorKeys.all, 'irrigation'] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks - خطافات الاستعلام
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch available crop types
 * خطاف لجلب أنواع المحاصيل المتاحة
 *
 * Retrieves the list of supported crops and their growth parameters.
 *
 * @returns Query result with crop information list
 */
export function useVSCrops() {
  return useQuery<CropInfo[]>({
    queryKey: virtualSensorKeys.crops(),
    queryFn: () => virtualSensorsApi.getCrops(),
    staleTime: 1000 * 60 * 60, // 1 hour - crop data rarely changes
  });
}

/**
 * Hook to fetch crop coefficient (Kc) for a specific crop
 * خطاف لجلب معامل المحصول لنوع محدد
 *
 * Retrieves Kc values by growth stage for irrigation calculations.
 *
 * @param cropType - The crop type identifier
 * @returns Query result with crop Kc data
 */
export function useCropKc(cropType: string) {
  return useQuery({
    queryKey: virtualSensorKeys.cropKc(cropType),
    queryFn: () => virtualSensorsApi.getCropKc(cropType),
    enabled: !!cropType,
    staleTime: 1000 * 60 * 60, // 1 hour - Kc values are static
  });
}

/**
 * Hook to fetch available soil types
 * خطاف لجلب أنواع التربة المتاحة
 *
 * Retrieves the list of supported soil types with hydraulic properties.
 *
 * @returns Query result with soil information list
 */
export function useVSSoils() {
  return useQuery<SoilInfo[]>({
    queryKey: virtualSensorKeys.soils(),
    queryFn: () => virtualSensorsApi.getSoils(),
    staleTime: 1000 * 60 * 60, // 1 hour - soil types rarely change
  });
}

/**
 * Hook to fetch available irrigation methods
 * خطاف لجلب طرق الري المتاحة
 *
 * Retrieves the list of supported irrigation methods and their efficiencies.
 *
 * @returns Query result with irrigation methods
 */
export function useIrrigationMethods() {
  return useQuery({
    queryKey: virtualSensorKeys.irrigationMethods(),
    queryFn: () => virtualSensorsApi.getIrrigationMethods(),
    staleTime: 1000 * 60 * 60, // 1 hour - methods rarely change
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks - خطافات الطفرة
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to calculate reference evapotranspiration (ET0)
 * خطاف لحساب التبخر-نتح المرجعي
 *
 * Calculates ET0 using the Penman-Monteith equation from weather data.
 *
 * @returns Mutation result with ET0 calculation
 */
export function useCalculateET0() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      temperature: number;
      humidity: number;
      windSpeed: number;
      solarRadiation: number;
      latitude: number;
      date?: string;
    }) => virtualSensorsApi.calculateET0(data),
    onSuccess: (_result: ET0Result) => {
      queryClient.invalidateQueries({ queryKey: virtualSensorKeys.et0() });
    },
  });
}

/**
 * Hook to calculate crop evapotranspiration (ETc)
 * خطاف لحساب التبخر-نتح الفعلي للمحصول
 *
 * Calculates ETc from ET0 and crop coefficient (Kc) values.
 *
 * @returns Mutation result with ETc calculation
 */
export function useCalculateETC() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      cropType: string;
      growthStage?: string;
      et0?: number;
      latitude?: number;
      date?: string;
    }) => virtualSensorsApi.calculateETC(data),
    onSuccess: (_result: ETCResult) => {
      queryClient.invalidateQueries({ queryKey: virtualSensorKeys.etc() });
    },
  });
}

/**
 * Hook to estimate soil moisture
 * خطاف لتقدير رطوبة التربة
 *
 * Estimates soil moisture using water balance and soil properties.
 *
 * @returns Mutation result with soil moisture estimate
 */
export function useEstimateSoilMoisture() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      soilType: string;
      lastIrrigation?: string;
      et0?: number;
      rainfall?: number;
    }) => virtualSensorsApi.estimateSoilMoisture(data),
    onSuccess: (_result: SoilMoistureEstimate) => {
      queryClient.invalidateQueries({ queryKey: virtualSensorKeys.soilMoisture() });
    },
  });
}

/**
 * Hook to get irrigation recommendation
 * خطاف للحصول على توصية الري
 *
 * Generates a detailed irrigation recommendation based on
 * crop, soil, weather, and field conditions.
 *
 * @returns Mutation result with irrigation recommendation
 */
export function useIrrigationRecommendation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { fieldId: string; cropType: string; soilType?: string }) =>
      virtualSensorsApi.getIrrigationRecommendation(data),
    onSuccess: (_result: IrrigationRecommendation) => {
      queryClient.invalidateQueries({ queryKey: virtualSensorKeys.irrigation() });
    },
  });
}

/**
 * Hook to perform a quick irrigation check
 * خطاف لإجراء فحص سريع للري
 *
 * Performs a simplified irrigation check with minimal input data.
 *
 * @returns Mutation result with quick irrigation check
 */
export function useQuickIrrigationCheck() {
  return useMutation({
    mutationFn: (data: { cropType: string; soilMoisture: number; temperature: number }) =>
      virtualSensorsApi.quickIrrigationCheck(data),
  });
}
