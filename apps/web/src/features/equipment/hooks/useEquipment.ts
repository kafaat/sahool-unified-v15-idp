/**
 * Equipment Feature - React Hooks
 * خطافات React لميزة المعدات
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { equipmentApi } from "../api";
import type {
  EquipmentFilters,
  EquipmentFormData,
  MaintenanceFormData,
} from "../types";

// Query Keys
export const equipmentKeys = {
  all: ["equipment"] as const,
  lists: () => [...equipmentKeys.all, "list"] as const,
  list: (filters?: EquipmentFilters) =>
    [...equipmentKeys.lists(), filters] as const,
  detail: (id: string) => [...equipmentKeys.all, "detail", id] as const,
  stats: () => [...equipmentKeys.all, "stats"] as const,
  maintenance: {
    all: ["maintenance"] as const,
    lists: () => [...equipmentKeys.maintenance.all, "list"] as const,
    list: (equipmentId?: string) =>
      [...equipmentKeys.maintenance.lists(), equipmentId] as const,
    detail: (id: string) =>
      [...equipmentKeys.maintenance.all, "detail", id] as const,
  },
};

/**
 * Hook to fetch equipment list
 */
export function useEquipment(filters?: EquipmentFilters) {
  return useQuery({
    queryKey: equipmentKeys.list(filters),
    queryFn: () => equipmentApi.getEquipment(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch single equipment
 */
export function useEquipmentDetails(id: string) {
  return useQuery({
    queryKey: equipmentKeys.detail(id),
    queryFn: () => equipmentApi.getEquipmentById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch equipment statistics
 */
export function useEquipmentStats() {
  return useQuery({
    queryKey: equipmentKeys.stats(),
    queryFn: () => equipmentApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook to create equipment
 */
export function useCreateEquipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: EquipmentFormData) => equipmentApi.createEquipment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: equipmentKeys.lists() });
      queryClient.invalidateQueries({ queryKey: equipmentKeys.stats() });
    },
  });
}

/**
 * Hook to update equipment
 */
export function useUpdateEquipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<EquipmentFormData>;
    }) => equipmentApi.updateEquipment(id, data),
    onSuccess: (updatedEquipment) => {
      queryClient.invalidateQueries({ queryKey: equipmentKeys.lists() });
      queryClient.setQueryData(
        equipmentKeys.detail(updatedEquipment.id),
        updatedEquipment,
      );
      queryClient.invalidateQueries({ queryKey: equipmentKeys.stats() });
    },
  });
}

/**
 * Hook to delete equipment
 */
export function useDeleteEquipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => equipmentApi.deleteEquipment(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({ queryKey: equipmentKeys.lists() });
      queryClient.removeQueries({ queryKey: equipmentKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: equipmentKeys.stats() });
    },
  });
}

/**
 * Hook to update equipment location
 */
export function useUpdateEquipmentLocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      location,
    }: {
      id: string;
      location: { latitude: number; longitude: number; fieldId?: string };
    }) => equipmentApi.updateLocation(id, location),
    onSuccess: (updatedEquipment) => {
      queryClient.setQueryData(
        equipmentKeys.detail(updatedEquipment.id),
        updatedEquipment,
      );
      queryClient.invalidateQueries({ queryKey: equipmentKeys.lists() });
    },
  });
}

/**
 * Hook to fetch maintenance records
 */
export function useMaintenanceRecords(equipmentId?: string) {
  return useQuery({
    queryKey: equipmentKeys.maintenance.list(equipmentId),
    queryFn: () => equipmentApi.getMaintenanceRecords(equipmentId),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Hook to fetch single maintenance record
 */
export function useMaintenanceDetails(id: string) {
  return useQuery({
    queryKey: equipmentKeys.maintenance.detail(id),
    queryFn: () => equipmentApi.getMaintenanceById(id),
    enabled: !!id,
  });
}

/**
 * Hook to create maintenance record
 */
export function useCreateMaintenance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: MaintenanceFormData) =>
      equipmentApi.createMaintenance(data),
    onSuccess: (newRecord) => {
      queryClient.invalidateQueries({
        queryKey: equipmentKeys.maintenance.lists(),
      });
      queryClient.invalidateQueries({
        queryKey: equipmentKeys.detail(newRecord.equipmentId),
      });
      queryClient.invalidateQueries({ queryKey: equipmentKeys.stats() });
    },
  });
}

/**
 * Hook to update maintenance record
 */
export function useUpdateMaintenance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<MaintenanceFormData>;
    }) => equipmentApi.updateMaintenance(id, data),
    onSuccess: (updatedRecord) => {
      queryClient.invalidateQueries({
        queryKey: equipmentKeys.maintenance.lists(),
      });
      queryClient.setQueryData(
        equipmentKeys.maintenance.detail(updatedRecord.id),
        updatedRecord,
      );
    },
  });
}

/**
 * Hook to complete maintenance
 */
export function useCompleteMaintenance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      equipmentApi.completeMaintenance(id, notes),
    onSuccess: (completedRecord) => {
      queryClient.invalidateQueries({
        queryKey: equipmentKeys.maintenance.lists(),
      });
      queryClient.setQueryData(
        equipmentKeys.maintenance.detail(completedRecord.id),
        completedRecord,
      );
      queryClient.invalidateQueries({
        queryKey: equipmentKeys.detail(completedRecord.equipmentId),
      });
      queryClient.invalidateQueries({ queryKey: equipmentKeys.stats() });
    },
  });
}

/**
 * Hook to delete maintenance record
 */
export function useDeleteMaintenance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => equipmentApi.deleteMaintenance(id),
    onSuccess: (_: void, id: string) => {
      queryClient.invalidateQueries({
        queryKey: equipmentKeys.maintenance.lists(),
      });
      queryClient.removeQueries({
        queryKey: equipmentKeys.maintenance.detail(id),
      });
      queryClient.invalidateQueries({ queryKey: equipmentKeys.stats() });
    },
  });
}
