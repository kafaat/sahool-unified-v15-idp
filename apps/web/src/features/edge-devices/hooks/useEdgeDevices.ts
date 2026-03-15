/**
 * Edge Devices Feature - React Hooks
 * خطافات React لميزة أجهزة الحافة
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { edgeApi } from "../api";
import type { EdgeDevice, EdgeFilters } from "../types";

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const edgeKeys = {
  all: ["edge-devices"] as const,
  lists: () => [...edgeKeys.all, "list"] as const,
  list: (filters?: EdgeFilters) => [...edgeKeys.lists(), filters] as const,
  detail: (id: string) => [...edgeKeys.all, "detail", id] as const,
  metrics: (id: string) => [...edgeKeys.all, "metrics", id] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks (Read Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch edge devices with optional filters
 * خطاف لجلب أجهزة الحافة مع فلاتر اختيارية
 */
export function useEdgeDevices(filters?: EdgeFilters) {
  return useQuery({
    queryKey: edgeKeys.list(filters),
    queryFn: () => edgeApi.getDevices(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch a single edge device by ID
 * خطاف لجلب جهاز حافة واحد بواسطة المعرف
 */
export function useEdgeDevice(id: string) {
  return useQuery({
    queryKey: edgeKeys.detail(id),
    queryFn: () => edgeApi.getDeviceById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch edge device metrics by ID
 * خطاف لجلب مقاييس جهاز الحافة بواسطة المعرف
 */
export function useEdgeDeviceMetrics(id: string) {
  return useQuery({
    queryKey: edgeKeys.metrics(id),
    queryFn: () => edgeApi.getDeviceMetrics(id),
    enabled: !!id,
    staleTime: 1000 * 30, // 30 seconds (metrics change frequently)
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mutation Hooks (Write Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to create a new edge device
 * خطاف لإنشاء جهاز حافة جديد
 */
export function useCreateEdgeDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<EdgeDevice, "id">) => edgeApi.createDevice(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: edgeKeys.lists() });
    },
  });
}

/**
 * Hook to update an edge device
 * خطاف لتحديث جهاز حافة
 */
export function useUpdateEdgeDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<EdgeDevice>;
    }) => edgeApi.updateDevice(id, data),
    onSuccess: (updatedDevice: EdgeDevice) => {
      queryClient.invalidateQueries({ queryKey: edgeKeys.lists() });
      queryClient.setQueryData(edgeKeys.detail(updatedDevice.id), updatedDevice);
    },
  });
}

/**
 * Hook to delete an edge device
 * خطاف لحذف جهاز حافة
 */
export function useDeleteEdgeDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => edgeApi.deleteDevice(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: edgeKeys.lists() });
      queryClient.removeQueries({ queryKey: edgeKeys.detail(id) });
      queryClient.removeQueries({ queryKey: edgeKeys.metrics(id) });
    },
  });
}

/**
 * Hook to deploy a model to an edge device
 * خطاف لنشر نموذج على جهاز حافة
 */
export function useDeployModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      deviceId,
      modelName,
      variant,
    }: {
      deviceId: string;
      modelName: string;
      variant?: string;
    }) => edgeApi.deployModel(deviceId, modelName, variant),
    onSuccess: (_: unknown, variables) => {
      queryClient.invalidateQueries({
        queryKey: edgeKeys.detail(variables.deviceId),
      });
      queryClient.invalidateQueries({
        queryKey: edgeKeys.metrics(variables.deviceId),
      });
    },
  });
}

/**
 * Hook to sync an edge device
 * خطاف لمزامنة جهاز حافة
 */
export function useSyncDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deviceId: string) => edgeApi.syncDevice(deviceId),
    onSuccess: (_: unknown, deviceId: string) => {
      queryClient.invalidateQueries({
        queryKey: edgeKeys.detail(deviceId),
      });
      queryClient.invalidateQueries({
        queryKey: edgeKeys.metrics(deviceId),
      });
    },
  });
}
